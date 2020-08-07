Name:           python3-warwick-rasa-camera
Version:        1.0.4
Release:        0
License:        GPL3
Summary:        Common backend code for the RASA prototype camera daemon
Url:            https://github.com/warwick-one-metre/rasa-camd
BuildArch:      noarch

%description
Part of the observatory software for the RASA prototype telescope.

python3-warwick-rasa-camera holds the common camera code.

%prep

rsync -av --exclude=build .. .

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --prefix=%{_prefix} --root=%{buildroot}

%files
%defattr(-,root,root,-)
%{python3_sitelib}/*

%changelog
