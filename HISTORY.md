## History

### 0.3.5

- Bump getschema version to 0.1.2 so it allows empty object (dict) entries

### 0.3.4

- Bug fix: Do the proper null check (thx @NiallRees)

### 0.3.3

- Bug fix: Don't overwrite config when arg value is none


### 0.3.2

- Fix the bug of requiring start_datetime even when state arg is present

### 0.3.1

- Fix the issue of schema row not wrapped with object
- Automatically convert date type to datetime type since date is not
  supported by schema.
- Better error handling when --start_datetime is missing.
- --catalog must be always set for sync (no more auto generate in sync)

### 0.3.0

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
