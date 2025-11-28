package version

import _ "embed"

//go:embed VERSION
var Version string

var VersionPrerelease string
