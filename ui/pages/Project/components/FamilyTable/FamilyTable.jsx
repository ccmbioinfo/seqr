import React from 'react'
import PropTypes from 'prop-types'
import styled from 'styled-components'
import { Table } from 'semantic-ui-react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'

import Family from 'shared/components/panel/family'
import ExportTableButton from 'shared/components/buttons/export-table/ExportTableButton'
import TableLoading from 'shared/components/table/TableLoading'
import { HorizontalSpacer } from 'shared/components/Spacers'

import { getVisibleSortedFamiliesWithIndividuals, getProjectDetailsIsLoading } from '../../selectors'
import TableHeaderRow from './header/TableHeaderRow'
import EmptyTableRow from './EmptyTableRow'
import IndividualRow from './IndividualRow'
import PageSelector from './PageSelector'


const ExportContainer = styled.span`
  float: right;
  padding-top: 15px;
`

const FamilyTable = ({ visibleFamilies, loading, headerStatus, showSearchLinks, fields, showInternalFilters, editCaseReview, exportUrls }) =>
  <div>
    <PageSelector />
    <ExportContainer>
      <ExportTableButton downloads={exportUrls} />
      <HorizontalSpacer width={45} />
    </ExportContainer>
    <Table celled striped padded>
      <TableHeaderRow headerStatus={headerStatus} showInternalFilters={showInternalFilters} />
      <Table.Body>
        {loading ? <TableLoading /> : null}
        {
          !loading && visibleFamilies.length > 0 ?
            visibleFamilies.map(family =>
              <Table.Row key={family.familyGuid}>
                <Table.Cell>
                  {[
                    <Family
                      key={family.familyGuid}
                      family={family}
                      showSearchLinks={showSearchLinks}
                      fields={fields}
                    />,
                    family.individuals.map(individual => (
                      <IndividualRow
                        key={individual.individualGuid}
                        family={family}
                        individual={individual}
                        editCaseReview={editCaseReview}
                      />),
                    ),
                  ]}
                </Table.Cell>
              </Table.Row>)
            : <EmptyTableRow />
        }
      </Table.Body>
      <Table.Footer><Table.Row><Table.HeaderCell /></Table.Row></Table.Footer>
    </Table>
  </div>


export { FamilyTable as FamilyTableComponent }

FamilyTable.propTypes = {
  visibleFamilies: PropTypes.array.isRequired,
  loading: PropTypes.bool,
  headerStatus: PropTypes.object,
  showInternalFilters: PropTypes.bool,
  editCaseReview: PropTypes.bool,
  exportUrls: PropTypes.array,
  fields: PropTypes.array,
  showSearchLinks: PropTypes.bool,
}

const mapStateToProps = (state, ownProps) => ({
  visibleFamilies: getVisibleSortedFamiliesWithIndividuals(state, ownProps),
  loading: getProjectDetailsIsLoading(state),
})

export default withRouter(connect(mapStateToProps)(FamilyTable))
