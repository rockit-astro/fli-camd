RPMBUILD = rpmbuild --define "_topdir %(pwd)/build" \
        --define "_builddir %{_topdir}" \
        --define "_rpmdir %{_topdir}" \
        --define "_srcrpmdir %{_topdir}" \
        --define "_sourcedir %(pwd)"

GIT_VERSION = $(shell git name-rev --name-only --tags --no-undefined HEAD 2>/dev/null || echo git-`git rev-parse --short HEAD`)
SERVER_VERSION=$(shell awk '/Version:/ { print $$2; }' observatory-fli-camera-server.spec)

all:
	mkdir -p build
	cp fli_camd fli_camd.bak
	awk '{sub("SOFTWARE_VERSION = .*$$","SOFTWARE_VERSION = \"$(SERVER_VERSION) ($(GIT_VERSION))\""); print $0}' fli_camd.bak > fli_camd
	${RPMBUILD} -ba observatory-fli-camera-server.spec
	${RPMBUILD} -ba observatory-fli-camera-client.spec
	${RPMBUILD} -ba python3-warwick-observatory-camera-fli.spec
	${RPMBUILD} -ba clasp-fli-camera-data.spec
	mv build/noarch/*.rpm .
	rm -rf build
	mv fli_camd.bak fli_camd

