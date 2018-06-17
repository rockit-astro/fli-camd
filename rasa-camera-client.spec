Name:      rasa-camera-client
Version:   2.1.1
Release:   0
Url:       https://github.com/warwick-one-metre/rasa-camd
Summary:   Camera control client for the RASA prototype telescope.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch
Requires:  python34, python34-Pyro4, python34-warwick-observatory-common, python34-warwick-rasa-camera

%description
Part of the observatory software for the RASA prototype telescope.

cam is a commandline utility for controlling the cameras.

%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}/etc/bash_completion.d
%{__install} %{_sourcedir}/cam %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/completion/cam %{buildroot}/etc/bash_completion.d/cam

%files
%defattr(0755,root,root,-)
%{_bindir}/cam
/etc/bash_completion.d/cam

%changelog
