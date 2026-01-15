# Metadata

This repository is used for storing Språkbanken Text's resource metadata as YAML files. When creating a new resource,
please place the YAML file in the correct directory under [/yaml](/yaml). You can use one of the available [YAML
templates](/yaml_templates) to get started. It is recommended to use a tool to perform a syntax check on your YAML
document (e.g., [this one](https://codebeautify.org/yaml-validator)) to avoid general errors in the YAML markup.

If you are comfortable with using the terminal, we also recommend that you use a JSON schema validation tool (e.g.,
[boon](https://github.com/santhosh-tekuri/boon/releases)) to validate your file against the provided [JSON
schema](/schema/metadata.json).

Please do **not** use this repository for storing data files (e.g., corpora, lexicons, etc.). Refer to the [instructions
on the Språkbanken Text web page](https://spraakbanken.gu.se/om/internt/teknik/metadata) for information on where to
store data files instead.

## Documentation

- [Instructions for creating metadata](https://spraakbanken.gu.se/om/internt/teknik/metadata) (requires login)
- [YAML templates](/yaml_templates)
- [Metadata API repository](https://github.com/spraakbanken/metadata-api)

## Information about some metadata fields

### Collections

A collection is a "meta" metadata entry used to summarize multiple resources. Collections are provided as YAML files.
The resource IDs belonging to a collection can either be supplied as a list in the YAML file (using the `resources` key)
or each resource can specify which collection(s) it belongs to in its YAML file (using the `in_collections` key, which
holds a list of collection IDs). The size of the collection is calculated automatically.

Resources referenced in a collection may include wildcards using simple glob-style patterns such as `*` and `?` to match
multiple resources. For example, the resource ID `kubhist-*` will match all resources with IDs that start with
`kubhist-`. It is also possible to supply a resource type prefix (e.g., `corpus/kubhist-*`) to only match resources of a
specific type.

### Unlisted

Resources with the attribute `"unlisted": true` will not be listed in the data list on the web page, but they can be
accessed directly via their URL. This is used as a quick and "dirty" versioning system.

### Successors

The `successors` attribute can be used for resources that have been superseded by one or more other resources (e.g.,
newer versions). This attribute holds a list of resource IDs.

### Hide resources

If `"hide_resources": true` is set, the resources belonging to this collection will not be listed in a table on the
collection web page.
