# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-04-13 21:59
from __future__ import unicode_literals
import json
from tqdm import tqdm

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import seqr.models

# Valid MIM numbers that are not in the seqr DB because they do not map to a valid gene
MIM_NUMBER_WHITELIST = [
    208500, 268000, 229850, 304050, 108800, 103220, 207950, 269860, 614688, 119530, 252350, 236750, 602346, 223370,
    604185, 604431, 119550, 600193, 212067,
]

# A couple invalid HPO terms seem to have passed through for Sherr and Peirce
NONSTANDARD_HPO_TERMS = {'HP:007737', 'HP:000729', 'HP:00729', 'HP:00HP:00729', "'HP:000729"}

# HPO terms that have been remapped to new IDs
HPO_ID_REMAP = {
    'HP:00030532': 'HP:0030532', 'HP:0008220': 'HP:0008163', 'HP:0001006': 'HP:0008070', 'HP:0002880': 'HP:0002098',
    'HP:0000057': 'HP:0008665', 'HP:0002281': 'HP:0002282', 'HP:0002459': 'HP:0012332', 'HP:0007087': 'HP:0001336',
    'HP:0000487': 'HP:0000486', 'HP:0004760': 'HP:0001671', 'HP:0001002': 'HP:0003758', 'HP:0002271': 'HP:0012332',
    'HP:0002564': 'HP:0030680', 'HP:0005901': 'HP:0002754', 'HP:0006525': 'HP:0002101', 'HP:0001380': 'HP:0001388',
    'HP:0007930': 'HP:0000286', 'HP:3000001': 'HP:0001627', 'HP:0001724': 'HP:0004942', 'HP:0002109': 'HP:0025426',
    'HP:0005111': 'HP:0004970', 'HP:0007702': 'HP:0000580', 'HP:0001587': 'HP:0008209', 'HP:0002229': 'HP:0002232',
    'HP:0005549': 'HP:0001875', 'HP:0000833': 'HP:0001952', 'HP:0005130': 'HP:0001723', 'HP:0006158': 'HP:0001187',
    'HP:0008012': 'HP:0000545', 'HP:0007868': 'HP:0000608', 'HP:0001379': 'HP:0002758'
}

# HPO terms that are obsolete but have no updated ID
OBSOLETE_HPO_IDS = ['HP:0200144', 'HP:0011607']


def update_phenotips_fields(apps, schema_editor):
    Individual = apps.get_model("seqr", "Individual")
    HumanPhenotypeOntology = apps.get_model("reference_data", "HumanPhenotypeOntology")
    Omim = apps.get_model("reference_data", "Omim")
    db_alias = schema_editor.connection.alias
    individuals = Individual.objects.using(db_alias).filter(
        phenotips_data__isnull=False).exclude(phenotips_data='').select_related('family')
    if individuals:
        from seqr.views.apis.phenotips_api import _update_individual_phenotips_fields, _get_parsed_feature
        hpo_map = {hpo.hpo_id: hpo for hpo in HumanPhenotypeOntology.objects.exclude(name__startswith='obsolete')}
        hpo_map.update({hpo.hpo_id: hpo for hpo in HumanPhenotypeOntology.objects.filter(hpo_id__in=OBSOLETE_HPO_IDS)})
        hpo_name_map = {hpo.name.upper(): hpo for hpo in hpo_map.values()}
        all_mim_ids = set(Omim.objects.values_list('phenotype_mim_number', flat=True))
        all_mim_ids.update(MIM_NUMBER_WHITELIST)
        miscarriages = []
        print('Updating  {} individuals'.format(len(individuals)))
        for indiv in tqdm(individuals, unit=' individuals'):
            phenotips_json = json.loads(indiv.phenotips_data)

            if (phenotips_json.get('family_history') or {}).get('miscarriages'):
                miscarriages.append(indiv.individual_id)

            nonstandard_features = []
            for feature in phenotips_json.get('nonstandard_features') or []:
                mapped = False
                parsed_label = map(lambda s: s.strip().upper(), feature['label'].split(','))
                for label in parsed_label:
                    if label.startswith('HP:'):
                        hpo_data = hpo_map.get(label)
                    else:
                        hpo_data = hpo_name_map.get(label)
                    if hpo_data:
                        mapped = True
                        if not phenotips_json.get('features'):
                            phenotips_json['features'] = []
                        phenotips_json['features'].append(_get_parsed_feature(feature, id=hpo_data.hpo_id))
                if not mapped:
                    nonstandard_features.append(feature)
            phenotips_json['nonstandard_features'] = nonstandard_features

            for feature in phenotips_json.get('features') or []:
                if feature['id'] in NONSTANDARD_HPO_TERMS:
                    feature['label'] = feature['id']
                    phenotips_json['nonstandard_features'].append(feature)
                    continue
                if feature['id'] in HPO_ID_REMAP:
                    feature['id'] = HPO_ID_REMAP[feature['id']]
                hpo_data = hpo_map.get(feature['id'])
                if not hpo_data:
                    raise Exception('Invalid HPO term for {}: {}'.format(indiv.individual_id, feature['id']))

            if phenotips_json.get('disorders'):
                mim_ids = map(lambda d: int(d['id'].lstrip('MIM:')), phenotips_json['disorders'])
                missing_ids = [mim_id for mim_id in mim_ids if mim_id not in all_mim_ids]
                if missing_ids:
                    raise Exception('Invalid MIM IDs for {}: {}'.format(
                        indiv.individual_id, ', '.join(map(str, missing_ids))))

            notes = phenotips_json.get('notes') or {}
            if notes.get('family_history'):
                if indiv.family.analysis_notes:
                    indiv.family.analysis_notes += '\n\n'
                else:
                    indiv.family.analysis_notes = ''
                indiv.family.analysis_notes += '__Family Health Conditions__: {}'.format(notes['family_history'])
                indiv.family.save()

            if notes.get('indication_for_referral'):
                if indiv.notes:
                    indiv.notes += '\n\n'
                else:
                    indiv.notes = ''
                indiv.notes += '__Indication for referral__: {}'.format(notes['indication_for_referral'])
            if notes.get('diagnosis_notes'):
                if indiv.notes:
                    indiv.notes += '\n\n'
                else:
                    indiv.notes = ''
                indiv.notes += '__Diagnosis Notes__: {}'.format(notes['diagnosis_notes'])

            prenatal = phenotips_json['prenatal_perinatal_history']
            if prenatal.get('paternal_age') or prenatal.get('maternal_age'):
                if indiv.notes:
                    indiv.notes += '\n\n'
                else:
                    indiv.notes = ''
                if prenatal.get('maternal_age'):
                    indiv.notes += '__Maternal Age__: {}'.format(prenatal['maternal_age'])
                    if prenatal.get('paternal_age'):
                        indiv.notes += '; '
                if prenatal.get('paternal_age'):
                    indiv.notes += '__Paternal Age__: {}'.format(prenatal['paternal_age'])

            _update_individual_phenotips_fields(indiv, phenotips_json)

            indiv.save()

        if miscarriages:
            print('The following {} individuals were flagged for miscarriages: {}'.format(
                len(miscarriages), ', '.join(miscarriages)))


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0009_auto_20200402_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='individual',
            name='absent_features',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='absent_nonstandard_features',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='affected_relatives',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='ar_donoregg',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='ar_donorsperm',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='ar_fertility_meds',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='ar_icsi',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='ar_iui',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='ar_ivf',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='ar_surrogacy',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='birth_year',
            field=seqr.models.YearField(choices=[
                (1900, 1900), (1901, 1901), (1902, 1902), (1903, 1903), (1904, 1904), (1905, 1905), (1906, 1906),
                (1907, 1907), (1908, 1908), (1909, 1909), (1910, 1910), (1911, 1911), (1912, 1912), (1913, 1913),
                (1914, 1914), (1915, 1915), (1916, 1916), (1917, 1917), (1918, 1918), (1919, 1919), (1920, 1920),
                (1921, 1921), (1922, 1922), (1923, 1923), (1924, 1924), (1925, 1925), (1926, 1926), (1927, 1927),
                (1928, 1928), (1929, 1929), (1930, 1930), (1931, 1931), (1932, 1932), (1933, 1933), (1934, 1934),
                (1935, 1935), (1936, 1936), (1937, 1937), (1938, 1938), (1939, 1939), (1940, 1940), (1941, 1941),
                (1942, 1942), (1943, 1943), (1944, 1944), (1945, 1945), (1946, 1946), (1947, 1947), (1948, 1948),
                (1949, 1949), (1950, 1950), (1951, 1951), (1952, 1952), (1953, 1953), (1954, 1954), (1955, 1955),
                (1956, 1956), (1957, 1957), (1958, 1958), (1959, 1959), (1960, 1960), (1961, 1961), (1962, 1962),
                (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969),
                (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976),
                (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983),
                (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990),
                (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997),
                (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004),
                (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011),
                (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018),
                (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025),
                (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029), (0, b'Unknown')], null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='candidate_genes',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='cosanguinity',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='individual',
            name='death_year',
            field=seqr.models.YearField(choices=[
                (1900, 1900), (1901, 1901), (1902, 1902), (1903, 1903), (1904, 1904), (1905, 1905), (1906, 1906),
                (1907, 1907), (1908, 1908), (1909, 1909), (1910, 1910), (1911, 1911), (1912, 1912), (1913, 1913),
                (1914, 1914), (1915, 1915), (1916, 1916), (1917, 1917), (1918, 1918), (1919, 1919), (1920, 1920),
                (1921, 1921), (1922, 1922), (1923, 1923), (1924, 1924), (1925, 1925), (1926, 1926), (1927, 1927),
                (1928, 1928), (1929, 1929), (1930, 1930), (1931, 1931), (1932, 1932), (1933, 1933), (1934, 1934),
                (1935, 1935), (1936, 1936), (1937, 1937), (1938, 1938), (1939, 1939), (1940, 1940), (1941, 1941),
                (1942, 1942), (1943, 1943), (1944, 1944), (1945, 1945), (1946, 1946), (1947, 1947), (1948, 1948),
                (1949, 1949), (1950, 1950), (1951, 1951), (1952, 1952), (1953, 1953), (1954, 1954), (1955, 1955),
                (1956, 1956), (1957, 1957), (1958, 1958), (1959, 1959), (1960, 1960), (1961, 1961), (1962, 1962),
                (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969),
                (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976),
                (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983),
                (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990),
                (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997),
                (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004),
                (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011),
                (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018),
                (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025),
                (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029), (0, b'Unknown')], null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='disorders',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=10), null=True, size=None),
        ),
        migrations.AddField(
            model_name='individual',
            name='expected_inheritance',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[
                (b'S', b'Sporadic'), (b'D', b'Autosomal dominant inheritance'),
                (b'L', b'Sex-limited autosomal dominant'), (b'A', b'Male-limited autosomal dominant'),
                (b'C', b'Autosomal dominant contiguous gene syndrome'), (b'R', b'Autosomal recessive inheritance'),
                (b'G', b'Gonosomal inheritance'), (b'X', b'X-linked inheritance'),
                (b'Z', b'X-linked recessive inheritance'), (b'Y', b'Y-linked inheritance'),
                (b'W', b'X-linked dominant inheritance'), (b'F', b'Multifactorial inheritance'),
                (b'M', b'Mitochondrial inheritance')], max_length=1), null=True, size=None),
        ),
        migrations.AddField(
            model_name='individual',
            name='features',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='maternal_ethnicity',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=40), null=True, size=None),
        ),
        migrations.AddField(
            model_name='individual',
            name='nonstandard_features',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='onset_age',
            field=models.CharField(choices=[
                (b'G', b'Congenital onset'), (b'E', b'Embryonal onset'), (b'F', b'Fetal onset'),
                (b'N', b'Neonatal onset'), (b'I', b'Infantile onset'), (b'C', b'Childhood onset'),
                (b'J', b'Juvenile onset'), (b'A', b'Adult onset'), (b'Y', b'Young adult onset'),
                (b'M', b'Middle age onset'), (b'L', b'Late onset')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='paternal_ethnicity',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=40), null=True, size=None),
        ),
        migrations.AddField(
            model_name='individual',
            name='rejected_genes',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.RunPython(update_phenotips_fields, reverse_code=migrations.RunPython.noop),
    ]
