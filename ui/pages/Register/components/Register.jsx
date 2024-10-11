import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { BooleanCheckbox } from 'shared/components/form/Inputs'
import { validators } from 'shared/components/form/FormHelpers'
import register from '../reducers'
import { UserFormContainer, UserForm } from './UserFormLayout'

const FIELDS = [
  { name: 'first_name', label: 'First Name', validate: validators.required },
  { name: 'last_name', label: 'Last Name', validate: validators.required },
  { name: 'email', label: 'Institutional Email Address', validate: validators.requiredEmail },
  { name: 'username', label: 'Username', validate: validators.required },
  { name: 'password', label: 'Password', type: 'password', validate: validators.requiredPassword },
  { name: 'affiliation', label: 'Affiliation', validate: validators.required },
  { name: 'referral', label: 'How did you hear about the CCM-seqr instance?', validate: validators.required },
  {
    name: 'check_1',
    component: BooleanCheckbox,
    validate: validators.required,
    label: (
      <label>
        I AM A HEALTH CARE PROFESSIONAL OR SCIENTIST WORKING WITH PATIENTS AFFECTED BY RARE DISORDERS.
      </label>
    ),
  },
  {
    name: 'check_2',
    component: BooleanCheckbox,
    validate: validators.required,
    label: (
      <label>
        NO ATTEMPT TO IDENTIFY INDIVIDUAL PATIENTS WILL BE UNDERTAKEN.
      </label>
    ),
  },
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
