#
# Ensembl module for Bio::EnsEMBL::Funcgen::DBSQL::ProbeSetAdaptor
#

=head1 LICENSE

Copyright [1999-2015] Wellcome Trust Sanger Institute and the EMBL-European Bioinformatics Institute
Copyright [2016-2020] EMBL-European Bioinformatics Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

=head1 CONTACT

  Please email comments or questions to the public Ensembl
  developers list at <http://lists.ensembl.org/mailman/listinfo/dev>.

  Questions may also be sent to the Ensembl help desk at
  <http://www.ensembl.org/Help/Contact>.

=head1 NAME

Bio::EnsEMBL::Funcgen::DBSQL::ProbeSetAdaptor - A database adaptor for fetching and
storing ProbeSet objects.

=head1 SYNOPSIS

 use Bio::EnsEMBL::Registry;
 use Bio::EnsEMBL::Funcgen::ProbeSet;


 my $reg = Bio::EnsEMBL::Registry->load_adaptors_from_db(-host    => 'ensembldb.ensembl.org',
                                                         -user    => 'anonymous');


 my $pset_a = Bio::EnsEMBL::Resgitry->get_adpator($species, 'funcgen', 'ProbeSet');

 #Fetching a probe_set by name
 my $probe_set = $pset_a->fetch_by_array_probe_set_name('Array-1', 'ProbeSet-1');

 ### Fetching probe_set with transcript annotations ###
 # Generated by the Ensembl array mapping pipeline

 my @probe_sets     = @{$pset_a->fetch_all_by_linked_Transcript($transcript)};

 #Note: Associated linkage annotation is stored in the associated DBEntries

=head1 DESCRIPTION

The ProbeSetAdaptor is a database adaptor for storing and retrieving
ProbeSet objects.

=head1 SEE ALSO

  Bio::EnsEMBL::Funcgen::Probe
  Bio::EnsEMBL::Funcgen::ProbeSet
  ensembl-funcgen/scripts/examples/microarray_annotation_example.pl

  Or for details on how to run the array mapping pipeline see:
  ensembl-funcgen/docs/array_mapping.txt

=cut

package Bio::EnsEMBL::Funcgen::DBSQL::ProbeSetAdaptor;

use strict;
use warnings;
use Bio::EnsEMBL::Utils::Exception qw( throw warning );
use Bio::EnsEMBL::Utils::Exception qw( deprecate );
use Bio::EnsEMBL::Funcgen::ProbeSet;
use Bio::EnsEMBL::Funcgen::DBSQL::BaseAdaptor;#DBI sql_types import

use base qw(Bio::EnsEMBL::Funcgen::DBSQL::BaseAdaptor);

=head2 fetch_by_array_probe_set_name

  Arg [1]    : string - name of array
  Arg [2]    : string - name of probe_set
  Example    : my $probe_set = $opsa->fetch_by_array_probe_set_name('Array-1', 'Probeset-1');
  Description: Returns a probe_set given the array name and probe_set name
               This will uniquely define a probe_set. Only one probe_set is ever returned.
  Returntype : Bio::EnsEMBL::ProbeSet
  Exceptions : None
  Caller     : General
  Status     : At Risk

=cut
sub fetch_by_array_probe_set_name {
  my ($self, $array_name, $probe_set_name) = @_;

  if(! ($array_name && $probe_set_name)){
    throw('Must provide array_name and probe_set_name arguments');
  }

  #Extend query tables
  $self->_tables([['probe', 'p'], ['array_chip', 'ac'], ['array', 'a']]);
  my $constraint = 'ps.name= ? AND ps.probe_set_id=p.probe_set_id AND p.array_chip_id=ac.array_chip_id AND ac.array_id=a.array_id AND a.name= ? GROUP by ps.probe_set_id';

  #bind params as we have unsafe string args
  $self->bind_param_generic_fetch($probe_set_name, SQL_VARCHAR);
  $self->bind_param_generic_fetch($array_name,    SQL_VARCHAR);

  my $pset =  $self->generic_fetch($constraint)->[0];
  $self->reset_true_tables;

  return $pset;
}

=head2 fetch_all_by_transcript_stable_id

  Arg [1]    : string - transcript stable id
  Example    : my $probe_set_list = $probe_set_adaptor->fetch_all_by_transcript_stable_id('ENST00000489935');
  Description: Fetches all probe_sets that have been mapped to this transcript by the 
               probe2transcript step in the probemapping pipeline.
  Returntype : Arrayref
  Caller     : General

=cut

sub fetch_all_by_transcript_stable_id {
  my $self = shift;
  my $transcript_stable_id = shift;

  my $probe_set_transcript_mappings = $self->db->get_ProbeSetTranscriptMappingAdaptor->fetch_all_by_transcript_stable_id($transcript_stable_id);
  
  if (! defined $probe_set_transcript_mappings) {
    return [];
  }
  
  my @probe_sets_mapped_to_transcript;
  foreach my $current_probe_set_transcript_mapping (@$probe_set_transcript_mappings) {
    push @probe_sets_mapped_to_transcript,
      $self->fetch_by_dbID($current_probe_set_transcript_mapping->probe_set_id);
  }
  return \@probe_sets_mapped_to_transcript;
}

=head2 fetch_all_by_name

  Arg [1]    : string - probe set name
  Example    : my @probes = @{$pdaa->fetch_all_by_name('ProbeSet1')};
  Description: Convenience method to re-instate the functionality of
               $core_dbentry_adpator->fetch_all_by_external_name('probe_set_name');
               WARNING: This may not be the probe_set you are expecting as
               probe_set names are not unqiue across arrays and vendors.
               These should ideally be validated using the attached array
               information or alternatively use fetch_by_array_probe_set_name
               Returns a probe with the given name.
  Returntype : Arrayref
  Exceptions : Throws if name not passed
  Caller     : General
  Status     : At Risk

=cut

sub fetch_all_by_name {
  my ($self, $name) = @_;

  throw('Must provide a probe_set name argument') if ! defined $name;
  $self->bind_param_generic_fetch($name, SQL_VARCHAR);

  return $self->generic_fetch('ps.name=?');
}

=head2 fetch_by_ProbeFeature

  Arg [1]    : Bio::EnsEMBL::ProbeFeature
  Example    : my $probe_set = $opsa->fetch_by_ProbeFeature($feature);
  Description: Returns the probe_set that created a particular feature.
  Returntype : Bio::EnsEMBL::ProbeSet
  Exceptions : Throws if argument is not a Bio::EnsEMBL::ProbeFeature object
  Caller     : General
  Status     : At Risk

=cut

sub fetch_by_ProbeFeature {
  my $self = shift;
  my $probe_feature = shift;
  
  $self->db->is_stored_and_valid('Bio::EnsEMBL::Funcgen::ProbeFeature', $probe_feature);

  # Extend query
  $self->_tables([['probe', 'p']]);
  my $probe_set =  $self->generic_fetch('p.probe_id='.$probe_feature->probe_id.' and p.probe_set_id=ps.probe_set_id GROUP by ps.probe_set_id')->[0];
  $self->reset_true_tables;
  return $probe_set;
}

=head2 fetch_all_by_Array

  Arg [1]    : Bio::EnsEMBL::Funcgen::Array
  Example    : my @probe_sets = @{$pset_adaptor->fetch_all_by_Array($array)};
  Description: Fetch all ProbeSets on a particular array.
  Returntype : Listref of Bio::EnsEMBL::ProbeSet objects.
  Exceptions : throws if arg is not valid or stored
  Caller     : General
  Status     : At Risk

=cut

sub fetch_all_by_Array {
  my $self  = shift;
  my $array = shift;

  if(! (ref($array) && $array->isa('Bio::EnsEMBL::Funcgen::Array') && $array->dbID())){
    throw('Need to pass a valid stored Bio::EnsEMBL::Funcgen::Array');
  }

  #get all array_chip_ids, for array and do a subselect statement with generic fetch
  my $constraint = (  " ps.probe_set_id in"
    ." ( SELECT distinct(p.probe_set_id)"
    ."   from probe p where"
    ."   p.array_chip_id IN (".join(",", @{$array->get_array_chip_ids()}).")"
    ." )" );

  return $self->generic_fetch($constraint);
}

=head2 _true_tables

  Args       : None
  Example    : None
  Description: Returns the names and aliases of the tables to use for queries.
  Returntype : List of listrefs of strings
  Exceptions : None
  Caller     : Internal
  Status     : At Risk

=cut

sub _true_tables {
  return ([ 'probe_set', 'ps' ]);
}

=head2 _columns

  Args       : None
  Example    : None
  Description: PROTECTED implementation of superclass abstract method.
               Returns a list of columns to use for queries.
  Returntype : List of strings
  Exceptions : None
  Caller     : Internal
  Status     : At Risk

=cut

sub _columns {
  return qw( ps.probe_set_id ps.name ps.size ps.family);
}

=head2 _objs_from_sth

  Arg [1]    : DBI statement handle object
  Example    : None
  Description: PROTECTED implementation of superclass abstract method.
               Creates ProbeSet objects from an executed DBI statement
               handle.
  Returntype : Listref of Bio::EnsEMBL::ProbeSet objects
  Exceptions : None
  Caller     : Internal
  Status     : At Risk

=cut

sub _objs_from_sth {
  my ($self, $sth) = @_;

  my (@result, $probe_set_id, $name, $size, $family);

  $sth->bind_columns( \$probe_set_id,  \$name, \$size, \$family);

  while ( $sth->fetch() ) {
  
    # New probe_set
    my $probe_set = Bio::EnsEMBL::Funcgen::ProbeSet->new(
      -dbID    => $probe_set_id,
      -name    => $name,
      -size    => $size,
      -family  => $family,
      -adaptor => $self,
    );
    push @result, $probe_set;
  }
  return \@result;
}

sub update {
  my $self = shift;
  my @probe_sets = @_;
  
  foreach my $current_probe_set (@probe_sets) {
    $self->_update_one($current_probe_set);
  }
}

sub _update_one {
  my $self = shift;
  my $probe_set = shift;

  my $sth = $self->prepare('update probe_set set name=?, size=?, family=? where probe_set_id=?');

  $sth->bind_param(1, $probe_set->name,   SQL_VARCHAR);
  $sth->bind_param(2, $probe_set->size,   SQL_INTEGER);
  $sth->bind_param(3, $probe_set->family, SQL_VARCHAR);
  $sth->bind_param(4, $probe_set->dbID,   SQL_INTEGER);

  $sth->execute();
}

=head2 store

  Arg [1]    : List of Bio::EnsEMBL::Funcgen::ProbeSet objects
  Example    : $opa->store($probe_set1, $probe_set2, $probe_set3);
  Description: Stores given ProbeSet objects in the database. Should only be
               called once per probe because no checks are made for duplicates.??? It certainly looks like there is :/
               Sets dbID and adaptor on the objects that it stores.
  Returntype : None
  Exceptions : Throws if arguments are not Probe objects
  Caller     : General
  Status     : At Risk

=cut

sub store {
  my ($self, @probe_sets) = @_;

  if (scalar @probe_sets == 0) {
    throw('Must call store with a list of Probe objects');
  }

  my $db = $self->db();

  PROBESET: foreach my $current_probe_set (@probe_sets) {

    if ( !ref $current_probe_set || !$current_probe_set->isa('Bio::EnsEMBL::Funcgen::ProbeSet') ) {
      throw('ProbeSet must be an ProbeSet object');
    }

    if ( $current_probe_set->is_stored($db) ) {
      warning('ProbeSet [' . $current_probe_set->dbID() . '] is already stored in the database');
      next PROBESET;
    }

    my $sth = $self->prepare("INSERT INTO probe_set (name, size, family) VALUES (?, ?, ?)");

    $sth->bind_param(1, $current_probe_set->name(),                     SQL_VARCHAR);
    $sth->bind_param(2, $current_probe_set->size(),                     SQL_INTEGER);
    $sth->bind_param(3, $current_probe_set->family(),                   SQL_VARCHAR);

    $sth->execute();
    
    $current_probe_set->dbID($self->last_insert_id);
    $current_probe_set->adaptor($self);
  }
  return \@probe_sets;
}

1;
