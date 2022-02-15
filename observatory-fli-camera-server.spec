Name:      observatory-fli-camera-server
Version:   20220215
Release:   0
Url:       https://github.com/warwick-one-metre/fli-camd
Summary:   Camera control server for FLI ML50100 camera.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch
Requires:  python3, python3-Pyro4, python3-numpy, python3-astropy, python3-pyserial, python3-warwick-observatory-common, python3-warwick-observatory-fli-camera

%description

%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_udevrulesdir}

%{__install} %{_sourcedir}/fli_camd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/fli_camd@.service %{buildroot}%{_unitdir}
%{__install} %{_sourcedir}/10-fliusb.rules %{buildroot}%{_udevrulesdir}
%{__install} %{_sourcedir}/10-fli-camera-timer.rules %{buildroot}%{_udevrulesdir}

%files
%defattr(0755,root,root,-)
%{_bindir}/fli_camd
%defattr(0644,root,root,-)
%{_udevrulesdir}/10-fliusb.rules
%{_udevrulesdir}/10-fli-camera-timer.rules
%{_unitdir}/fli_camd@.service

%changelog
