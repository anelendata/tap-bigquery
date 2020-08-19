## History

### 0.3.0b0

- Handle multiple streams
- Support state (bookmark)
- No need to use "CAST(<column_name> as datetime)" in datetime_key
  See sample_config.json
- Support Stitch Data's sdc timestamp keys
- Use singer library functions to write out the schema, records, and state

### 0.2.0

- Add state message to satisfy any singer target
- Correct the way etl timestamp are exposed from the tap: switch from second in float type to commonoly used microseconds timestamp

### 0.1.0

- Pilot (non-release)
