export default [
  {
    type: 'text',
    name: 'name',
    fullName: 'Batch name',
    constraints: {
      length: {
        minimum: 4,
        maximum: 50
      },
      type: 'string',
      format: {
        pattern: '[a-zA-Z0-9-+_,]+',
        flags: 'i'
      }
    }
  },
  {
    type: 'number',
    name: 'width',
    fullName: 'Images width',
    default: 1000,
    constraints: {
      numericality: {
        greaterThanOrEqualTo: 100,
        lessThanOrEqualTo: 1000
      },
      type: 'integer'
    }
  },
  {
    type: 'number',
    name: 'height',
    fullName: 'Images height',
    default: 1000,
    constraints: {
      numericality: {
        greaterThanOrEqualTo: 100,
        lessThanOrEqualTo: 1000
      },
      type: 'integer'
    }
  },
  {
    type: 'number',
    name: 'zoomLevel',
    fullName: 'Zoom level',
    default: 18,
    constraints: {
      numericality: {
        greaterThanOrEqualTo: 3,
        lessThanOrEqualTo: 21
      },
      type: 'integer'
    }
  }
]
