%global pkgvers 0
%global scdate0 20241009
%global schash0 32b2456e37eae5ee379f626c65c8509eaec16230
%global branch0 master
%global source0 https://github.com/chipsalliance/verible.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           verible
Version:        0.0
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        Suite of SystemVerilog developer tools
License:        Apache

URL:            https://chipsalliance.github.io/verible

Patch0:         verible-build.patch

BuildRequires:  git bazel6 flex bison python3
%if 0%{?rhel} == 8
BuildRequires:  gcc-toolset-9-gcc-c++
%else
BuildRequires:  gcc-c++
%endif

%global debug_package %{nil}
%global _lto_cflags %{nil}
%undefine _hardened_build
%undefine _annotated_build

%description
Verible is a suite of SystemVerilog developer tools,
including a parser, style-linter, and formatter.


%prep
%setup -T -c -n %{name}
git clone --depth 1 -n -b %{branch0} %{source0} %{name}
git -C %{name} fetch --depth 1 origin %{schash0}
git -C %{name} reset --hard %{schash0}
git -C %{name} log --format=fuller
%patch -P 0 -p1 -b .build~


%build
pushd %{name}
# set env
export TMP=/tmp
export TEST_TMPDIR="%{_builddir}/%{name}"
export GIT_DATE="git%{sshort0}"
export GIT_VERSION="%{version}-%{scdate0}.%{pkgvers}"
# build
%if 0%{?rhel} == 8
source scl_source enable gcc-toolset-9
%endif
bazel build \
    --subcommands \
    --explain=build.log \
    --show_result=2147483647 \
    --local_ram_resources=32768 \
    --jobs %{_smp_build_ncpus} \
    --verbose_failures \
    --incompatible_use_python_toolchains \
    --//bazel:use_local_flex_bison //...
popd


%install
pushd %{name}
# set env
export TMP=/tmp
export TEST_TMPDIR="%{_builddir}/%{name}"
export GIT_DATE="git%{sshort0}"
export GIT_VERSION="%{version}-%{scdate0}.%{pkgvers}"
# install
mkdir -p {buildroot}%{_bindir}/
%if 0%{?rhel} == 8
source scl_source enable gcc-toolset-9
%endif
bazel run \
    --subcommands \
    --explain=install.log \
    --show_result=2147483647 \
    --local_ram_resources=32768 \
    --jobs %{_smp_build_ncpus} \
    --verbose_failures \
    --incompatible_use_python_toolchains \
    --//bazel:use_local_flex_bison \
    -c opt :install -- %{buildroot}%{_bindir}/
popd


%files
%doc %{name}/README.md
%doc %{name}/doc
%license %{name}/LICENSE
%{_bindir}/*


%changelog
* Wed Apr 20 2022 Cristian Balint <cristian.balint@gmail.com>
- github update releases
