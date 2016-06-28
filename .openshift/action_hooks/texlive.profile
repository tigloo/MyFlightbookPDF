#
# texlive.profile for automatic deployment on OpenShift
# Based on manual run of TeXLive installer.
#
selected_scheme scheme-custom
TEXDIR .
TEXMFCONFIG $TEXMFSYSCONFIG
TEXMFHOME $TEXMFLOCAL
TEXMFLOCAL ./texmf-local
TEXMFSYSCONFIG ./texmf-config
TEXMFSYSVAR ./texmf-var
TEXMFVAR $TEXMFSYSVAR
binary_x86_64-linux 1
collection-basic 1
collection-fontsrecommended 1
collection-langarabic 1
collection-langcjk 1
collection-langcyrillic 1
collection-langczechslovak 1
collection-langenglish 1
collection-langeuropean 1
collection-langfrench 1
collection-langgerman 1
collection-langgreek 1
collection-langindic 1
collection-langitalian 1
collection-langpolish 1
collection-langportuguese 1
collection-langspanish 1
collection-latex 1
collection-luatex 1
collection-xetex 1
in_place 0
option_adjustrepo 1
option_autobackup 1
option_backupdir tlpkg/backups
option_desktop_integration 
option_doc 1
option_file_assocs 
option_fmt 1
option_letter 0
option_menu_integration 
option_path 
option_post_code 1
option_src 1
option_sys_bin /usr/local/bin
option_sys_info /usr/local/share/info
option_sys_man /usr/local/share/man
option_w32_multi_user 1
option_write18_restricted 1
portable 1
