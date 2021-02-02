{ buildPythonPackage
, fetchPypi
, jinja2
, lib
, markdown2
, markupsafe
, pygments
}:

buildPythonPackage rec {
  pname = "pdoc";
  version = "4.0.0";
  format = "wheel";

  src = fetchPypi {
    inherit pname version;
    python = "py3";
    format = "wheel";
    sha256 = "sha256:08svgsnc4yknnf9flcqbb6k3jc4g0aiscxm23vvngwsm4k6mk2gj";
  };

  propagatedBuildInputs = [
    jinja2
    markdown2
    markupsafe
    pygments
  ];

  meta = with lib; {
    description = "API documentation for Python projects";
    homepage = "https://pdoc.dev/";
    license = licenses.unlicense;
    maintainers = [];
  };
}
