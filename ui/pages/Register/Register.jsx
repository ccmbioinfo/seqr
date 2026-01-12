import React from 'react'
import PropTypes from 'prop-types'
import { Route, Switch } from 'react-router-dom'

import { Error404 } from 'shared/components/page/Errors'
import Register from './components/Register'

const RegisterPage = ({ match }) => (
  <Switch>
    <Route key="register" exact path={match.url} component={Register} />
    <Route component={Error404} />
  </Switch>
)

RegisterPage.propTypes = {
  match: PropTypes.object,
}

export default RegisterPage
