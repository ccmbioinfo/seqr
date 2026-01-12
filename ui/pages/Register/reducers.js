import queryString from 'query-string'

import { HttpRequestHelper } from 'shared/utils/httpRequestHelper'

const redirectNext = () => {
  // Redirect to next page or home page
  window.location.href = `${window.location.origin}${queryString.parse(window.location.search).next || ''}`
}

// Data actions

const register = values => () => new HttpRequestHelper('/api/register', redirectNext).post(values)

export default register
