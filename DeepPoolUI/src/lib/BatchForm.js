export default [
  {
    type: 'number',
    name: 'coverage',
    fullName: 'Task coverage',
    default: 0.005,
    step: 0.005,
    constraints: {
      numericality: {
        greaterThanOrEqualTo: 0,
        lessThanOrEqualTo: 1
      },
      type: 'number'
    }
  },
  {
    type: 'number',
    name: 'sleep_min',
    fullName: 'Minimum sleep time',
    default: 0,
    constraints: {
      numericality: {
        greaterThanOrEqualTo: 0,
        lessThanOrEqualTo: 1000
      },
      type: 'integer'
    }
  },
  {
    type: 'number',
    name: 'sleep_max',
    fullName: 'Maximum sleep time',
    default: 3,
    constraints: {
      numericality: {
        greaterThanOrEqualTo: 0,
        lessThanOrEqualTo: 1000
      },
      type: 'integer'
    }
  }
]
