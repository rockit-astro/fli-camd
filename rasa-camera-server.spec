Name:      rasa-camera-server
Version:   2.1.8
Release:   0
Url:       https://github.com/warwick-one-metre/rasa-camd
Summary:   Camera control server for the RASA prototype telescope.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch

%if 0%{?centos_ver}
Requires:  python34, python34-Pyro4, python34-numpy, python34-astropy, python34-warwick-observatory-common, python34-warwick-rasa-camera, rasa-libfli, observatory-log-client, %{?systemd_requires}
%endif

%description
Part of the observatory software for the RASA prototype telescope.

camd interfaces with and wraps the FLI camera and exposes it via Pyro.

%build
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_udevrulesdir}

%{__install} %{_sourcedir}/camd %{buildroot}%{_bindir}
%{__install} %{_sourcedir}/rasa_camd.service %{buildroot}%{_unitdir}
%{__install} %{_sourcedir}/10-fliusb.rules %{buildroot}%{_udevrulesdir}
%{__install} %{_sourcedir}/10-rasa-camera-timer.rules %{buildroot}%{_udevrulesdir}

%post
%systemd_post rasa_camd.service

%preun
%systemd_preun rasa_camd.service

%postun
%systemd_postun_with_restart rasa_camd.service

%files
%defattr(0755,root,root,-)
%{_bindir}/camd
%defattr(0644,root,root,-)
%{_udevrulesdir}/10-fliusb.rules
%{_udevrulesdir}/10-rasa-camera-timer.rules
%{_unitdir}/rasa_camd.service

%changelog
