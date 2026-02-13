# Copyright 2026 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

%if !(0%{?fedora} >= 36)
%global _user_tmpfilesdir %{_datadir}/user-tmpfiles.d
%endif

Name: podman
Epoch: 100
Version: 5.8.0
Release: 1%{?dist}
Summary: Daemon-less container engine for managing containers, pods and images
License: Apache-2.0
URL: https://github.com/containers/podman/tags
Source0: %{name}_%{version}.orig.tar.gz
%if 0%{?rhel} == 7
BuildRequires: devtoolset-11
BuildRequires: devtoolset-11-gcc
BuildRequires: devtoolset-11-gcc-c++
BuildRequires: devtoolset-11-libatomic-devel
%endif
BuildRequires: glib2-devel
BuildRequires: glibc-static
BuildRequires: golang-1.26
BuildRequires: gpgme-devel
BuildRequires: libassuan-devel
BuildRequires: libgpg-error-devel
BuildRequires: libseccomp-devel
BuildRequires: make
BuildRequires: pkgconfig
BuildRequires: systemd-devel
BuildRequires: tzdata
Requires: catatonit
Requires: conmon
Requires: containernetworking-plugins
Requires: containers-common
Requires: iptables
Requires: oci-runtime
Requires: tzdata

%description
Podman is a container engine for managing pods, containers, and
container images. It is a standalone tool and it directly manipulates
containers without the need of a container engine daemon. Podman is able
to interact with container images create in buildah, cri-o, and skopeo,
as they all share the same datastore backend.

%prep
%setup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .
%autopatch -p1

%build
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-11/enable
%endif
mkdir -p bin
set -ex && \
    export CGO_ENABLED=1 && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp systemd selinux" \
        -o ./bin/podman ./cmd/podman && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp systemd selinux remote" \
        -o ./bin/podman-remote ./cmd/podman && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp systemd selinux" \
        -o ./bin/rootlessport ./cmd/rootlessport && \
    go build \
        -mod vendor -buildmode pie -v \
        -ldflags "-s -w" \
        -tags "netgo osusergo exclude_graphdriver_devicemapper exclude_graphdriver_btrfs containers_image_openpgp seccomp systemd selinux" \
        -o ./bin/quadlet ./cmd/quadlet

%install
install -Dpm755 -d %{buildroot}%{_sysconfdir}/profile.d
install -Dpm755 -d %{buildroot}%{_bindir}
install -Dpm755 -d %{buildroot}%{_libdir}/systemd/system-generators
install -Dpm755 -d %{buildroot}%{_libdir}/systemd/user-generators
install -Dpm755 -d %{buildroot}%{_libexecdir}/podman
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/podman
install -Dpm755 -t %{buildroot}%{_bindir}/ bin/podman-remote
install -Dpm755 -t %{buildroot}%{_libexecdir}/podman/ bin/rootlessport
install -Dpm755 -t %{buildroot}%{_libexecdir}/podman/ bin/quadlet
ln -sf %{_libexecdir}/podman/quadlet %{buildroot}%{_libdir}/systemd/system-generators/podman-system-generator
ln -sf %{_libexecdir}/podman/quadlet %{buildroot}%{_libdir}/systemd/user-generators/podman-user-generator
DESTDIR=%{buildroot} \
PREFIX=%{_prefix} \
BINDIR=%{_bindir} \
ETCDIR=%{_sysconfdir} \
SYSTEMDDIR=%{_unitdir} \
USERSYSTEMDDIR=%{_userunitdir} \
    make install.completions install.systemd install.docker

%package docker
Summary: Emulate Docker CLI using podman
Requires: podman = %{epoch}:%{version}-%{release}
Conflicts: docker
Conflicts: docker-ce
Conflicts: docker-ce-cli
Conflicts: docker-ee
Conflicts: docker-ee-cli
Conflicts: docker-latest
Conflicts: docker.io
Conflicts: moby-cli
Conflicts: moby-engine

%description docker
This package installs a script named docker that emulates the Docker CLI
by executes podman commands, it also creates links between all Docker
CLI man pages and podman.

%files
%license LICENSE
%dir %{_libdir}/systemd
%dir %{_libdir}/systemd/system-generators
%dir %{_libdir}/systemd/user-generators
%dir %{_libexecdir}/podman
%dir %{_prefix}/share/fish
%dir %{_prefix}/share/fish/vendor_completions.d
%{_bindir}/podman
%{_bindir}/podman-remote
%{_libdir}/systemd/system-generators/*
%{_libdir}/systemd/user-generators/*
%{_libexecdir}/podman/quadlet
%{_libexecdir}/podman/rootlessport
%{_prefix}/share/bash-completion/completions/*
%{_prefix}/share/fish/vendor_completions.d/*
%{_prefix}/share/zsh/site-functions/*
%{_unitdir}/*
%{_userunitdir}/*
%{_sysconfdir}/profile.d/*

%files docker
%dir %{_user_tmpfilesdir}
%{_bindir}/docker
%{_tmpfilesdir}/podman-docker.conf
%{_user_tmpfilesdir}/podman-docker.conf

%changelog
