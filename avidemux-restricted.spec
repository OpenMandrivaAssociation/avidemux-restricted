%define libname		%mklibname %{name}
%define filename %{name}_%{version}
%define _disable_ld_no_undefined 1
%define _disable_lto 1

#define ffmpeg_version 2.7.7

#############################
# Hardcore PLF build
# bcond_with or bcond_without
%bcond_with plf
#############################

%if %with plf
%define distsuffix plf
# make EVR of plf build higher than regular to allow update, needed with rpm5 mkrel
%define extrarelsuffix plf
%endif

Summary:	A free video editor
Name:		avidemux
Version:	2.7.2
Release:	1%{?extrarelsuffix}
License:	GPLv2+
Group:		Video
Url:		http://fixounet.free.fr/avidemux
Source0:	http://www.fosshub.com/Avidemux.html/avidemux_%{version}.tar.gz
#Source1:	ffmpeg-%{ffmpeg_version}.tar.bz2
Source100:	%{name}.rpmlintrc
Patch1:		avidemux-2.6.12-compile.patch
Patch2:		avidemux-2.5.1-opencore-check.patch
Patch3:		avidemux-jack-underlinking.patch
Patch4:		avidemux-fix-cmake.patch
#Patch5:		avidemux-2.6.8-ffmpeg-1.2.12.patch
#Patch6:		avidemux-2.7.0-c++.patch
BuildRequires:	cmake
BuildRequires:	dos2unix
BuildRequires:	imagemagick
BuildRequires:	nasm
BuildRequires:	xsltproc
BuildRequires:	yasm
BuildRequires:	gettext-devel
BuildRequires:	a52dec-devel
BuildRequires: lame-devel
BuildRequires:  pkgconfig(Qt5Core)
BuildRequires:  pkgconfig(Qt5Gui)
BuildRequires:  pkgconfig(Qt5OpenGL)
BuildRequires:  pkgconfig(Qt5Script)
BuildRequires:  pkgconfig(Qt5Widgets)
BuildRequires:  qmake5
BuildRequires:  qt5-linguist-tools
BuildRequires:  qt5-qttools
BuildRequires:	%{_lib}qt5gui5-vnc
BuildRequires:	pkgconfig(jack)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(libva)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(mad)
BuildRequires:	pkgconfig(samplerate)
BuildRequires:	pkgconfig(sdl2)
BuildRequires:	pkgconfig(vorbis)
BuildRequires:	pkgconfig(xv)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires: pkgconfig(libass)
BuildRequires: pkgconfig(vpx)
BuildRequires: pkgconfig(twolame)
BuildRequires: pkgconfig(opus)	
BuildRequires: pkgconfig(ffnvcodec)
# not packaged yet:
#BuildRequires:  libaften-devel
%if %with plf
BuildRequires:	libfaac-devel
BuildRequires:	libfaad2-devel
BuildRequires: pkgconfig(libdca)
BuildRequires:	libxvid-devel
BuildRequires:	pkgconfig(opencore-amrnb)
BuildRequires:	pkgconfig(opencore-amrwb)
BuildRequires:	pkgconfig(x264)
BuildRequires: pkgconfig(x265)
%endif
BuildRequires:	pkgconfig(glu)
Requires:	avidemux-ui

%description
Avidemux is a free video editor designed for simple cutting,
filtering and encoding tasks.It supports many file types, including
AVI, DVD compatible MPEG files, MP4 and ASF, using a variety of
codecs. Tasks can be automated using projects, job queue and
powerful scripting capabilities.

%if %with plf
This package is in restricted because this build has support for codecs
covered by software patents.
%endif

%package -n	%{libname}
Summary:	Shared libraries for %{name}

%description -n	%{libname}
Shared libraries for %{name}.

%package	devel
Summary:	Header files for %{name}
Requires:	%{libname} = %{version}
Requires:	pkgconfig(vdpau)
Obsoletes:	%{name}-qt-devel < %{version}-%{release}
Obsoletes:	%{name}-cli-devel < %{version}-%{release}

%description	devel
Header files for %{name}.

%package	cli
Summary:	Command line interface for %{name}
%rename		%{name}
Recommends:	%{name}-plugins
Recommends:	%{name}-cli-plugins

%description	cli
This package contains the command-line interface for %{name}.

%package	qt
Summary:	Qt5 graphical user interface for %{name}
%rename		%{name}
Recommends:	%{name}-plugins
Recommends:	%{name}-qt-plugins

%description	qt
This package contains the Qt5 graphical user interface for %{name}.

%package	plugins
Summary:	Plugins for %{name}

%description	plugins
This package contains the common plugins for %{name}.

%package	cli-plugins
Summary:	Plugins for %{name}-cli

%description	cli-plugins
This package contains the plugins for the %{name} command-line interface.

%package	qt-plugins
Summary:	Plugins for %{name}-qt

%description	qt-plugins
This package contains the plugins for the %{name} graphical user interface.

%if %with plf
This package is in restricted because this build has support for codecs
covered by software patents.
%endif

%prep
%setup -qn %{filename}

dos2unix avidemux/common/ADM_render/CMakeLists.txt

#sed -i 's/set(FFMPEG_VERSION "2.7.6")/set(FFMPEG_VERSION "%{ffmpeg_version}")/' cmake/admFFmpegBuild.cmake
#rm -f avidemux_core/ffmpeg_package/ffmpeg-*.tar.bz2
#cp %{SOURCE1} avidemux_core/ffmpeg_package/

%apply_patches


%build


%setup_compile_flags
export CFLAGS="%{optflags} -fno-strict-aliasing"
export CXXFLAGS="%{optflags} -fno-strict-aliasing"

export PATH=%{_libdir}/qt5/bin:$PATH

bash bootStrap.bash \
     --with-core \
     --with-cli \
     --with-plugins \
     --with-system-libass \
     --with-system-liba52 \
     --with-system-libmad

%install
cp -a install/* %{buildroot}
mkdir -p %{buildroot}%{_mandir}/man1
install -m 644 man/avidemux.1 %{buildroot}%{_mandir}/man1
chrpath --delete %{buildroot}%{_libdir}/*.so*
chrpath --delete %{buildroot}%{_libdir}/ADM_plugins6/*/*.so
chrpath --delete %{buildroot}%{_bindir}/*
rm -rf %{buildroot}%{_datadir}/ADM6_addons


%files -n %{libname}
%{_libdir}/libADM_audio*.so
%{_libdir}/libADM_core*.so
%{_libdir}/libADM6*.so.*

%files devel
%{_includedir}/%{name}

%files cli
%{_mandir}/man1/avidemux.1*
%{_bindir}/avidemux3_cli
%{_libdir}/libADM_UI_Cli6.so
%{_libdir}/libADM_render6_cli.so

%files qt
%{_bindir}/avidemux3_qt5
%{_bindir}/avidemux3_jobs_qt5
%{_libdir}/libADM_UIQT56.so
%{_libdir}/libADM_render6_QT5.so
%{_libdir}/libADM_openGLQT56.so
%dir %{_datadir}/avidemux6
%dir %{_datadir}/avidemux6/qt5
%{_datadir}/metainfo/org.avidemux.Avidemux.appdata.xml
%{_iconsdir}/hicolor/128x128/apps/org.avidemux.Avidemux.png
%{_datadir}/applications/org.avidemux.Avidemux.desktop

%files plugins
%dir %{_libdir}/ADM_plugins6
%dir %{_libdir}/ADM_plugins6/*
%{_libdir}/ADM_plugins6/*/*
%exclude %{_libdir}/ADM_plugins6/videoFilters/cli/*.so
%exclude %{_libdir}/ADM_plugins6/videoFilters/qt5/*.so

%files cli-plugins
%{_libdir}/ADM_plugins6/videoFilters/cli/*.so

%files qt-plugins
%dir %{_datadir}/avidemux6/qt5/i18n
%{_datadir}/avidemux6/qt5/i18n/*.qm
%{_libdir}/ADM_plugins6/videoFilters/qt5/*.so
