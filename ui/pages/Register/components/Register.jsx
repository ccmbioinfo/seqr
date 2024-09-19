import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { validators } from 'shared/components/form/FormHelpers'
import register from '../reducers'
import { UserFormContainer, UserForm } from './UserFormLayout'

const FIELDS = [
  { name: 'username', label: 'Username', validate: validators.required },
  { name: 'first_name', label: 'First Name', validate: validators.required },
  { name: 'last_name', label: 'Last Name', validate: validators.required },
  { name: 'email', label: 'Email Address', type: 'email', validate: validators.required },
  { name: 'password', label: 'Password', type: 'password', validate: validators.required },
]

const Register = ({ onSubmit }) => (
  <UserFormContainer header="Create a new account">
    <UserForm
      onSubmit={onSubmit}
      modalName="register"
      fields={FIELDS}
      submitButtonText="Create Account"
    />
    <Link to="/login">Already Have an Account?</Link>
  </UserFormContainer>
)

Register.propTypes = {
  onSubmit: PropTypes.func,
}

const mapDispatchToProps = {
  onSubmit: register,
}

export default connect(null, mapDispatchToProps)(Register)
