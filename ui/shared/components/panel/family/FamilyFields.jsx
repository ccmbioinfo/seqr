import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Popup, Icon } from 'semantic-ui-react'
import styled from 'styled-components'

import { loadUserOptions, loadProjectAnalysisGroups, updateFamily } from 'redux/rootReducer'
import {
  getSamplesByFamily,
  getUserOptionsIsLoading,
  getHasActiveSearchableSampleByFamily,
  getUserOptions,
  getProjectAnalysisGroupOptions,
  getAnalysisGroupsByFamily,
  getAnalysisGroupIsLoading,
} from 'redux/selectors'

import DispatchRequestButton from '../../buttons/DispatchRequestButton'
import TagFieldView from '../view-fields/TagFieldView'
import Sample from '../sample'
import { ColoredIcon } from '../../StyledComponents'
import { Select } from '../../form/Inputs'
import DataLoader from '../../DataLoader'

const NoWrap = styled.div`
  white-space: nowrap;
`

const BaseFirstSample = React.memo(({ firstFamilySample, compact, hasActiveVariantSample }) => (
  <Sample
    loadedSample={firstFamilySample}
    hoverDetails={compact ? 'first loaded' : null}
    isOutdated={!hasActiveVariantSample}
  />
))

BaseFirstSample.propTypes = {
  firstFamilySample: PropTypes.object,
  compact: PropTypes.bool,
  hasActiveVariantSample: PropTypes.bool,
}

const mapSampleDispatchToProps = (state, ownProps) => ({
  firstFamilySample: (getSamplesByFamily(state)[ownProps.familyGuid] || [])[0],
  hasActiveVariantSample: (getHasActiveSearchableSampleByFamily(state)[ownProps.familyGuid] || {}).isActive,
})

export const FirstSample = connect(mapSampleDispatchToProps)(BaseFirstSample)

const BaseAnalystEmailDropdown = React.memo(({ load, loading, onChange, value, ...props }) => (
  <DataLoader load={load} loading={false} content>
    <Select
      loading={loading}
      additionLabel="Assigned Analyst: "
      onChange={onChange}
      value={value}
      placeholder="Unassigned"
      search
      {...props}
    />
  </DataLoader>
))

BaseAnalystEmailDropdown.propTypes = {
  load: PropTypes.func,
  loading: PropTypes.bool,
  onChange: PropTypes.func,
  value: PropTypes.object,
}

const mapDropdownStateToProps = state => ({
  loading: getUserOptionsIsLoading(state),
  options: getUserOptions(state),
})

const mapDropdownDispatchToProps = (dispatch, ownProps) => ({
  load: () => dispatch(loadUserOptions(ownProps.meta.data.formId)),
})

export const AnalystEmailDropdown = connect(
  mapDropdownStateToProps, mapDropdownDispatchToProps,
)(BaseAnalystEmailDropdown)

export const analysisStatusIcon = (
  value, compact, { analysisStatusLastModifiedBy, analysisStatusLastModifiedDate },
) => {
  const icon = <ColoredIcon name="stop" color={value.color} />
  if (!compact && !analysisStatusLastModifiedDate) {
    return icon
  }
  return (
    <Popup
      trigger={icon}
      content={
        <div>
          {compact && value.name}
          {analysisStatusLastModifiedDate && (
            <i>
              {compact && <br />}
              {`Changed on ${new Date(analysisStatusLastModifiedDate).toLocaleDateString()}`}
              <br />
              {`by ${analysisStatusLastModifiedBy}`}
            </i>
          )}
        </div>
      }
      position="top center"
    />
  )
}

const SNP_TYPE = 'SNP'
const ANALYSED_BY_TYPES = [
  [SNP_TYPE, 'WES/WGS'],
  ['SV', 'gCNV/SV'],
  ['RNA', 'RNAseq'],
  ['MT', 'Mitochondrial'],
  ['STR', 'STR'],
]

const BaseAnalysedBy = React.memo(({ analysedByList, compact, onSubmit }) => {
  const analysedByType = analysedByList.reduce(
    (acc, analysedBy) => ({ ...acc, [analysedBy.dataType]: [...(acc[analysedBy.dataType] || []), analysedBy] }), {},
  )

  if (compact) {
    return [...(analysedByType[SNP_TYPE] || []).reduce(
      (acc, { createdBy }) => acc.add(createdBy), new Set(),
    )].map(
      analysedByUser => <NoWrap key={analysedByUser}>{analysedByUser}</NoWrap>,
    )
  }

  return ANALYSED_BY_TYPES.map(typeConfig => (
    <div key={typeConfig[0]}>
      <b>{`${typeConfig[1]}: `}</b>
      {(analysedByType[typeConfig[0]] || []).map(
        analysedBy => `${analysedBy.createdBy} (${new Date(analysedBy.lastModifiedDate).toLocaleDateString()})`,
      ).join(', ')}
      &nbsp;&nbsp;
      <DispatchRequestButton
        buttonContent={<Icon link size="small" name="plus" />}
        onSubmit={onSubmit(typeConfig[0])}
        confirmDialog={`Are you sure you want to add that you analysed this family for ${typeConfig[1]} data?`}
      />
    </div>
  ))
})

BaseAnalysedBy.propTypes = {
  analysedByList: PropTypes.arrayOf(PropTypes.object),
  compact: PropTypes.bool,
  onSubmit: PropTypes.func,
}

const mapDispatchToProps = (dispatch, ownProps) => ({
  onSubmit: dataType => () => {
    dispatch(updateFamily({ dataType, familyGuid: ownProps.familyGuid, familyField: 'analysed_by' }))
  },
})

export const AnalysedBy = connect(null, mapDispatchToProps)(BaseAnalysedBy)

const BaseAnalysisGroups = React.memo(({ load, loading, ...props }) => (
  <DataLoader load={load} loading={loading} content>
    <TagFieldView {...props} />
  </DataLoader>
))

BaseAnalysisGroups.propTypes = {
  load: PropTypes.func,
  loading: PropTypes.bool,
}

const mapGroupsStateToProps = (state, ownProps) => ({
  fieldValue: getAnalysisGroupsByFamily(state)[ownProps.initialValues.familyGuid],
  loading: getAnalysisGroupIsLoading(state),
  tagOptions: getProjectAnalysisGroupOptions(state)[ownProps.initialValues.projectGuid] || [],
})

const mapGroupsDispatchToProps = (dispatch, ownProps) => ({
  load: () => dispatch(loadProjectAnalysisGroups(ownProps.initialValues.projectGuid)),
})

export const AnalysisGroups = connect(mapGroupsStateToProps, mapGroupsDispatchToProps)(BaseAnalysisGroups)
