%define filename %{name}_%{version}

#############################
# Hardcore PLF build
# bcond_with or bcond_without
%bcond_without plf
#############################

%if %with plf
%define distsuffix plf
# make EVR of plf build higher than regular to allow update, needed with rpm5 mkrel
%define extrarelsuffix plf
%endif

Name:		avidemux
Version:	2.5.6
Release:	3%{?extrarelsuffix}
Summary:	A free video editor
License:	GPLv2+
Group:		Video
Url:		http://fixounet.free.fr/avidemux
Source0:	http://downloads.sourceforge.net/project/%{name}/%{name}/%{version}/%{filename}.tar.gz
Patch2:		avidemux-2.5.1-opencore-check.patch
Patch3:		avidemux-jack-underlinking.patch
Patch4:		avidemux-fix-cmake.patch
Patch5:		avidemux-mpeg2enc-underlinking.patch
Patch6:		CVE-2011-3893.patch
Patch7:		CVE-2011-3895.patch
Patch8:		CVE-2012-0947.patch
BuildRequires:	cmake
BuildRequires:	imagemagick
BuildRequires:	libxslt-proc
BuildRequires:	nasm
BuildRequires:	qt4-linguist
BuildRequires:	yasm
BuildRequires:	gettext-devel
BuildRequires:	liba52dec-devel
BuildRequires:	qt4-devel
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(esound)
BuildRequires:	pkgconfig(jack)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(libva)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(mad)
BuildRequires:	pkgconfig(samplerate)
BuildRequires:	pkgconfig(sdl)
BuildRequires:	pkgconfig(vorbis)
BuildRequires:	pkgconfig(xv)
# not packaged yet:
#BuildRequires:  libaften-devel
%if %with plf
BuildRequires:	libfaac-devel
BuildRequires:	libfaad2-devel
BuildRequires:	liblame-devel
BuildRequires:	libxvid-devel
BuildRequires:	pkgconfig(opencore-amrnb)
BuildRequires:	pkgconfig(opencore-amrwb)
BuildRequires:	pkgconfig(x264)
%endif
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

%package gtk
Summary:	A free video editor - GTK GUI
Group:		Video
Requires:	gtk+2.0 >= 2.6.0
Requires:	%{name} = %{version}-%{release}
Provides:	avidemux-ui = %{version}-%{release}

%description gtk
Avidemux is a free video editor. This package contains the
version with a graphical user interface based on GTK.

%package qt
Summary:	A free video editor - Qt4 GUI
Group:		Video
Requires:	%{name} = %{version}-%{release}
Provides:	avidemux-ui = %{version}-%{release}

%description qt
Avidemux is a free video editor. This package contains the
version with a graphical user interface based on Qt4.

%package cli
Summary:	A free video editor - command-line version
Group:		Video
Requires:	%{name} = %{version}-%{release}
Provides:	avidemux-ui = %{version}-%{release}

%description cli
Avidemux is a free video editor. This package contains the
version with a command-line interface.

%if %with plf
This package is in restricted because this build has support for codecs
covered by software patents.
%endif

%prep
%setup -q -n %{filename}
%patch2 -p1
%patch3 -p1
%patch4 -p0
%patch5 -p1

pushd avidemux/ADM_libraries

tar -xjf ffmpeg-0.9.tar.bz2 && rm -f ffmpeg-0.9.tar.bz2
pushd ffmpeg-0.9
%patch6 -p1
%patch7 -p1
%patch8 -p1
popd
tar -cjf ffmpeg-0.9.tar.bz2 ffmpeg-0.9 && rm -rf ffmpeg-0.9
popd

# libdir is nicely hardcoded
sed -i 's,Dir="lib",Dir="%{_lib}",' avidemux/main.cpp avidemux/ADM_core/src/ADM_fileio.cpp
grep -q '"%{_lib}"' avidemux/main.cpp
grep -q '"%{_lib}"' avidemux/ADM_core/src/ADM_fileio.cpp

%build
#gw 2.5.4 has linking problems in plugins/ADM_videoFilters/AvsFilter
#   	      	      	   and in plugins/ADM_videoFilters/Logo/
%define _disable_ld_no_undefined 1
%cmake
make

# plugin build expects libraries to be already installed; we fake a prefix
# in build/ by symlinking all libraries to build/lib/
mkdir -p %{_lib}
cd %{_lib}
find ../avidemux -name '*.so*' | xargs ln -sft .
cd ../../plugins
%cmake -DAVIDEMUX_SOURCE_DIR=%{_builddir}/%{filename} -DAVIDEMUX_CORECONFIG_DIR=%{_builddir}/%{filename}/build/config -DAVIDEMUX_INSTALL_PREFIX=%{_builddir}/%{filename}/build
make


%install
cd build
%makeinstall_std
mkdir -p %{buildroot}%{_libdir}
cd ..

cd plugins/build
%makeinstall_std
#gw install this manually:
cp ADM_videoEncoder/ADM_vidEnc_mpeg2enc/mpeg2enc/libmpeg2enc.so \
  ADM_videoEncoder/common/pluginOptions/libADM_vidEnc_pluginOptions.so \
  ADM_videoEncoder/common/xvidRateCtl/libADM_xvidRateCtl.so %{buildroot}%{_libdir}
cd ../..

# icons
install -d -m755 %{buildroot}%{_liconsdir}
install -d -m755 %{buildroot}%{_iconsdir}
install -d -m755 %{buildroot}%{_miconsdir}
convert avidemux_icon.png -resize 48x48 %{buildroot}%{_liconsdir}/%{name}.png
convert avidemux_icon.png -resize 32x32 %{buildroot}%{_iconsdir}/%{name}.png
convert avidemux_icon.png -resize 16x16 %{buildroot}%{_miconsdir}/%{name}.png

# menu
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}-gtk.desktop << EOF
[Desktop Entry]
Name=Avidemux
Comment=A free video editor
Exec=%{_bindir}/%{name}2_gtk %U
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=AudioVideo;Video;AudioVideoEditing;GTK;
EOF
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}-qt.desktop << EOF
[Desktop Entry]
Name=Avidemux
Comment=A free video editor
Exec=%{_bindir}/%{name}2_qt4 %U
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=AudioVideo;Video;AudioVideoEditing;Qt;
EOF

rm -rf %{buildroot}%{_datadir}/locale/klingon

%find_lang %{name}

%files -f %{name}.lang
%doc AUTHORS
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_libdir}/libADM5*
%{_libdir}/libADM_core*
%{_libdir}/libADM_smjs.so
%{_libdir}/libADM_vidEnc_pluginOptions.so
%{_libdir}/libADM_xvidRateCtl.so
%{_libdir}/libmpeg2enc.so
%dir %{_libdir}/ADM_plugins
%dir %{_libdir}/ADM_plugins/audioDecoder
%{_libdir}/ADM_plugins/audioDecoder/libADM_ad_Mad.so
%{_libdir}/ADM_plugins/audioDecoder/libADM_ad_a52.so
%if %with plf
%{_libdir}/ADM_plugins/audioDecoder/libADM_ad_opencore_amrnb.so
%{_libdir}/ADM_plugins/audioDecoder/libADM_ad_opencore_amrwb.so
%{_libdir}/ADM_plugins/audioDecoder/libADM_ad_faad.so
%endif
%{_libdir}/ADM_plugins/audioDecoder/libADM_ad_vorbis.so
%dir %{_libdir}/ADM_plugins/audioDevices
%{_libdir}/ADM_plugins/audioDevices/libADM_av_alsa.so
%{_libdir}/ADM_plugins/audioDevices/libADM_av_esd.so
%{_libdir}/ADM_plugins/audioDevices/libADM_av_jack.so
%{_libdir}/ADM_plugins/audioDevices/libADM_av_oss.so
%{_libdir}/ADM_plugins/audioDevices/libADM_av_pulseAudioSimple.so
%{_libdir}/ADM_plugins/audioDevices/libADM_av_sdl.so
%dir %{_libdir}/ADM_plugins/audioEncoders
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_lav_ac3.so
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_lav_mp2.so
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_pcm.so
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_twolame.so
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_vorbis.so
%dir %{_libdir}/ADM_plugins/videoEncoder
%if %with plf
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_faac.so
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_lame.so
%{_libdir}/ADM_plugins/videoEncoder/libADM_vidEnc_x264.so
%{_libdir}/ADM_plugins/videoEncoder/x264/*.xml
%{_libdir}/ADM_plugins/videoEncoder/x264/*.xsd
%endif
%{_libdir}/ADM_plugins/videoEncoder/libADM_vidEnc_xvid.so
%dir %{_libdir}/ADM_plugins/videoEncoder/xvid
%{_libdir}/ADM_plugins/videoEncoder/xvid/*.xsd
%endif
%dir %{_libdir}/ADM_plugins/videoEncoder/avcodec
%{_libdir}/ADM_plugins/videoEncoder/avcodec/*.xsd
%dir %{_libdir}/ADM_plugins/videoEncoder/avcodec/mpeg-?
%{_libdir}/ADM_plugins/videoEncoder/avcodec/mpeg-?/*.xml
%{_libdir}/ADM_plugins/videoEncoder/libADM_vidEnc_avcodec.so
%{_libdir}/ADM_plugins/videoEncoder/libADM_vidEnc_mpeg2enc.so
%dir %{_libdir}/ADM_plugins/videoEncoder/mpeg2enc
%{_libdir}/ADM_plugins/videoEncoder/mpeg2enc/*.xsd
%dir %{_libdir}/ADM_plugins/videoEncoder/mpeg2enc/mpeg-?
%{_libdir}/ADM_plugins/videoEncoder/mpeg2enc/mpeg-?/*.xml
%dir %{_libdir}/ADM_plugins/videoFilter
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Deinterlace.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Delta.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Denoise.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_FluxSmooth.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Mosaic.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Pulldown.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Stabilize.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Tisophote.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Whirl.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_addborders.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_avsfilter.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_blackenBorders.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_blendDgBob.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_blendRemoval.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_decimate.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_denoise3d.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_denoise3dhq.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_dropOut.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_fade.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_fastconvolutiongauss.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_fastconvolutionmean.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_fastconvolutionmedian.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_fastconvolutionsharpen.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_forcedPP.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_hzStackField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_keepEvenField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_keepOddField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_kernelDeint.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_largemedian.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_lavDeinterlace.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_logo.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_lumaonly.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mSharpen.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mSmooth.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mcdeint.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mergeField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_palShift.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_resampleFps.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_reverse.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_rotate.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_separateField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_smartPalShift.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_smartSwapField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_soften.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_ssa.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_stackField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_swapField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_swapuv.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_tdeint.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_telecide.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_unstackField.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_vflip.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_vlad.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_yadif.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vidChromaU.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vidChromaV.so
%{_datadir}/ADM_scripts/
%dir %{_datadir}/ADM_addons/
%{_datadir}/ADM_addons/avsfilter

%files gtk
%{_bindir}/avidemux2_gtk
%{_datadir}/applications/mandriva-avidemux-gtk.desktop
%{_libdir}/libADM_render_gtk.so
%{_libdir}/libADM_UIGtk.so
%if %with plf
%{_libdir}/ADM_plugins/videoEncoder/x264/libADM_vidEnc_x264_Gtk.so
%{_libdir}/ADM_plugins/videoEncoder/xvid/libADM_vidEnc_Xvid_Gtk.so
%endif
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Crop_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_asharp_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_avisynthResize_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_chromaShift_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_cnr2_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_colorYUV_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_contrast_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_eq2_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_equalizer_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_hue_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mpdelogo_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mplayerResize_gtk.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_sub_gtk.so

%files qt
%{_bindir}/avidemux2_qt4
%{_datadir}/applications/mandriva-avidemux-qt.desktop
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/i18n
%{_datadir}/%{name}/i18n/*.qm
%{_libdir}/libADM_render_qt4.so
%{_libdir}/libADM_UIQT4.so
%if %with plf
%{_libdir}/ADM_plugins/videoEncoder/x264/libADM_vidEnc_x264_Qt.so
%{_libdir}/ADM_plugins/videoEncoder/xvid/libADM_vidEnc_Xvid_Qt.so
%endif
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_crop_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_asharp_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_avisynthResize_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_chromaShift_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_cnr2_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_colorYUV_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_contrast_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_curveEditor_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_eq2_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_equalizer_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_hue_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mpdelogo_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mplayerResize_qt4.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_sub_qt4.so

%files cli
%doc README
%{_bindir}/avidemux2_cli
%{_libdir}/libADM_render_cli.so
%{_libdir}/libADM_UICli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_Hue_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_asharp_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_avisynthResize_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_chromashift_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_cnr2_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_colorYUV_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_contrast_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_crop_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_eq2_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_equalizer_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mpdelogo_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_mplayerResize_cli.so
%{_libdir}/ADM_plugins/videoFilter/libADM_vf_sub_cli.so


