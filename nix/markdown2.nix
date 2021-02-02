{ lib, buildPythonPackage, fetchPypi }:

buildPythonPackage rec {
  pname = "markdown2";
  version = "2.4.0";

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256:06wvhai41in8xdvwmn97d6d0fyvlhsqyj0agd27zdrj4wpq6kmr8";
  };

  meta = with lib; {
    description = "A fast and complete Python implementation of Markdown";
    homepage =  "https://github.com/trentm/python-markdown2";
    license = licenses.mit;
    maintainers = with maintainers; [ hbunke ];
  };
}
