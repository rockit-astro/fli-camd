Name:      clasp-fli-camera-data
Version:   20220128
Release:   0
Url:       https://github.com/warwick-one-metre/fli-camd
Summary:   Camera configuration for CLASP telescope.
License:   GPL-3.0
Group:     Unspecified
BuildArch: noarch

%description

%build
mkdir -p %{buildroot}%{_sysconfdir}/camd
%{__install} %{_sourcedir}/fli1.json %{buildroot}%{_sysconfdir}/camd

%files
%defattr(0644,root,root,-)
%{_sysconfdir}/camd/fli1.json

%changelog
