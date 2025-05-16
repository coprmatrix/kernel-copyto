Name: kernel-copyto
Version: 17
Release: 1
Summary: kernel copyto configurations for kernel-install
License: GPL-3.0-or-later
BuildArch: noarch

%description
%{summary}.

Requires: coreutils

%install
mkdir -p %{buildroot}%{_sysconfdir}/kernel/install.d



mkdir -p %{buildroot}%{_sysconfdir}/kernel/install.d
mkdir -p %{buildroot}%{_bindir}

cat << 'EOF' > %{buildroot}%{_sysconfdir}/kernel/install.d/52-%{name}.conf
#!/bin/sh
. %{_sysconfdir}/kernel-copyto.conf

if $enable; then
    echo "$1 $2 $3 $4"
    if test "$1" == "add" ; then
        (
            kernel-copyto --version "$2" --old_kernel="$4"
        )
    fi
fi
EOF

cat << 'EOF' > %{buildroot}%{_sysconfdir}/%{name}.conf
copydir=/boot
kernel=vmlinuz
initrd=initramfs.img
old_kernel=/lib/modules/%v/vmlinuz
old_initrd=initramfs-%v.img
command='ln -sfvr'
EOF

cat << 'EOF' > %{buildroot}%{_bindir}/%{name}
#!/bin/sh
while true; do
  case "$1" in
  --*)
    typeset  "${1:2}=$2"
    shift
    shift
  ;;
  *) break;;
  esac
done

. %{_sysconfdir}/kernel-copyto.conf
version="${version:-$(uname -r)}"
bootdir="${bootdir:-/boot}"
cd "${bootdir}"

format(){
  echo -n "$(echo -n "$1" | sed "s~%v~${version}~g; s~%%~%~g")" 
}

old_initrd="$(realpath "$(format ${old_initrd:-"initrd-%v"})")"
old_kernel="$(realpath "$(format ${old_kernel:-"vmlinuz-%v"})")"

copydir="${copydir:-"${bootdir}/efi"}"
mkdir -p "${copydir}" || :
cd "${copydir}"

initrd="$(realpath --no-symlinks $(format "${initrd:-initrd.img}"))"
kernel="$(realpath --no-symlinks $(format "${kernel:-kernel}"))"

command="${command:-"cp -Tfvp"}"

if [ -f "${old_initrd}" ]; then
    eval "${command} '${old_initrd}' '$(format ${initrd})'"
fi
if [ -f "$old_kernel" ]; then
    eval "${command} '${old_kernel}' '$(format ${kernel})'"
fi


EOF

%files
%attr(0755, root, root) %{_bindir}/%{name}
%attr(0644, root, root) %config %{_sysconfdir}/%{name}.conf
%attr(0644, root, root) %config %{_sysconfdir}/kernel/install.d/52-%{name}.conf
%dir %{_sysconfdir}/kernel/install.d/
%dir %{_sysconfdir}/kernel/

