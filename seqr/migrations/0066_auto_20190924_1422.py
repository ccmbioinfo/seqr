# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-24 14:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


def variant_note_to_multi_saved_variants(apps, schema_editor):
    VariantNote = apps.get_model("seqr", "VariantNote")
    db_alias = schema_editor.connection.alias
    variant_notes = VariantNote.objects.using(db_alias).all()
    print('Updating saved_variants for {} variant notes'.format(len(variant_notes)))
    for variant_note in variant_notes:
        saved_variant = variant_note.saved_variant
        if saved_variant is None:
            saved_variants = []
        else:
            saved_variants = [saved_variant]
        variant_note.saved_variants = saved_variants
        variant_note.save()


def variant_note_to_single_saved_variant(apps, schema_editor):
    VariantNote = apps.get_model("seqr", "VariantNote")
    db_alias = schema_editor.connection.alias
    variant_notes = VariantNote.objects.using(db_alias).all()
    print('Updating saved_variant for {} variant notes'.format(len(variant_notes)))
    for variant_note in variant_notes:
        variant_note.saved_variant = variant_note.saved_variants.first()
        variant_note.save()


def variant_tag_to_multi_saved_variants(apps, schema_editor):
    VariantTag = apps.get_model("seqr", "VariantTag")
    db_alias = schema_editor.connection.alias
    variant_tags = VariantTag.objects.using(db_alias).all()
    print('Updating saved_variants for {} variant tags'.format(len(variant_tags)))
    for variant_tag in variant_tags:
        curr_variant_tag = variant_tag.saved_variant
        if curr_variant_tag is None:
            variants_tag = []
        else:
            variants_tag = [curr_variant_tag]
        variant_tag.saved_variants = variants_tag
        variant_tag.save()


def variant_tag_to_single_saved_variant(apps, schema_editor):
    VariantTag = apps.get_model("seqr", "VariantTag")
    db_alias = schema_editor.connection.alias
    variant_tags = VariantTag.objects.using(db_alias).all()
    print('Updating saved_variant for {} variant tags'.format(len(variant_tags)))
    for variant_tag in variant_tags:
        variant_tag.saved_variant = variant_tag.saved_variants.first()
        variant_tag.save()


def variant_functional_data_to_multi_saved_variants(apps, schema_editor):
    VariantFunctionalData = apps.get_model("seqr", "VariantFunctionalData")
    db_alias = schema_editor.connection.alias
    all_functional_data = VariantFunctionalData.objects.using(db_alias).all()
    print('Updating saved_variants for {} functional data'.format(len(all_functional_data)))
    for functional_data in all_functional_data:
        variant_functional_data = functional_data.saved_variant
        if variant_functional_data is None:
            variants_functional_data = []
        else:
            variants_functional_data = [variant_functional_data]
        functional_data.saved_variants = variants_functional_data
        functional_data.save()


def variant_functional_data_to_single_saved_variant(apps, schema_editor):
    VariantFunctionalData = apps.get_model("seqr", "VariantFunctionalData")
    db_alias = schema_editor.connection.alias
    all_functional_data = VariantFunctionalData.objects.using(db_alias).all()
    print('Updating saved_variant for {} functional data'.format(len(all_functional_data)))
    for functional_data in all_functional_data:
        functional_data.saved_variant = functional_data.saved_variants.first()
        functional_data.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        # ('seqr', '0001_squashed_0067_remove_project_custom_reference_populations'),
    ]

    operations = [
        migrations.AddField(
            model_name='variantnote',
            name='saved_variants',
            field=models.ManyToManyField(to='seqr.SavedVariant'),
        ),
        migrations.RunPython(variant_note_to_multi_saved_variants, reverse_code=variant_note_to_single_saved_variant),
        migrations.AddField(
            model_name='variantfunctionaldata',
            name='saved_variants',
            field=models.ManyToManyField(to='seqr.SavedVariant'),
        ),
        migrations.RunPython(variant_functional_data_to_multi_saved_variants,
                             reverse_code=variant_functional_data_to_single_saved_variant),
        migrations.AddField(
            model_name='varianttag',
            name='saved_variants',
            field=models.ManyToManyField(to='seqr.SavedVariant'),
        ),
        migrations.RunPython(variant_tag_to_multi_saved_variants, reverse_code=variant_tag_to_single_saved_variant),
        migrations.AlterUniqueTogether(
            name='variantfunctionaldata',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='varianttag',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='variantnote',
            name='saved_variant',
        ),
        migrations.RemoveField(
            model_name='variantfunctionaldata',
            name='saved_variant',
        ),
        migrations.RemoveField(
            model_name='varianttag',
            name='saved_variant',
        ),
    ]
