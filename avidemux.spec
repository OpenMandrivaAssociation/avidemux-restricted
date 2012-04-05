%define	name	avidemux
%define	Name	Avidemux
%define version 2.5.5
%define rel 4
%define pre 0
%if %pre
%define filename %{name}_%{version}_preview%{pre}
%define release %mkrel 0.preview%{pre}.%{rel}
%else 
%define filename %{name}_%{version}
%define release %mkrel %{rel}
%endif

%bcond_with plf
%define with_x264 0

%if %with plf
%define distsuffix plf
%if %mdvver >= 201100
# make EVR of plf build higher than regular to allow update, needed with rpm5 mkrel
%define extrarelsuffix plf
%endif
%define with_x264 1
%endif

%define	pkgsummary	A free video editor

Name:		%{name}
Version:	%{version}
Release:	%{release}%{?extrarelsuffix}
Summary:	%{pkgsummary}
Source0:	http://downloads.sourceforge.net/project/%name/%name/%version/%{filename}.tar.gz
Patch2:		avidemux-2.5.1-opencore-check.patch
Patch3:		avidemux-jack-underlinking.patch
Patch5:		avidemux-mpeg2enc-underlinking.patch
#fix build with x264 0.115
Patch6:		avidemux-2.5.5-x264.patch
#disable arts
Patch7:		avidemux-2.5.5-arts.patch
License:	GPLv2+
Group:		Video
Url:		http://fixounet.free.fr/avidemux
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildRequires:	gtk+2-devel >= 2.6.0
BuildRequires:	qt4-devel qt4-linguist
BuildRequires:	SDL-devel
BuildRequires:	nasm
BuildRequires:	libxml2-devel
BuildRequires:	libmad-devel
BuildRequires:	liba52dec-devel
BuildRequires:	libvorbis-devel
BuildRequires:	esound-devel
BuildRequires:	libjack-devel
BuildRequires:	libpulseaudio-devel
BuildRequires:	libsamplerate-devel
BuildRequires:	gettext-devel
BuildRequires:	libxv-devel
BuildRequires:	libva-devel
BuildRequires:	cmake
BuildRequires:	libxslt-proc
# not packaged yet:
#BuildRequires:  libaften-devel
%if %with plf
BuildRequires:	libxvid-devel
BuildRequires:	liblame-devel
BuildRequires:	libfaad2-devel
BuildRequires:	libfaac-devel
%if %with_x264
BuildRequires:	x264-devel >= 0.67
%endif
BuildRequires:  opencore-amr-devel
%endif
BuildRequires:	imagemagick
BuildRequires:	yasm
Requires: avidemux-ui

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
Summary:	%{pkgsummary} - GTK GUI
Group:		Video
Requires: gtk+2.0 >= 2.6.0
Requires: %{name} = %{version}-%{release}
Provides: avidemux-ui = %{version}-%{release}

%description gtk
Avidemux is a free video editor. This package contains the
version with a graphical user interface based on GTK.

%package qt
Summary:	%{pkgsummary} - Qt4 GUI
Group:		Video
Requires: %{name} = %{version}-%{release}
Provides: avidemux-ui = %{version}-%{release}

%description qt
Avidemux is a free video editor. This package contains the
version with a graphical user interface based on Qt4.

%package cli
Summary:	%{pkgsummary} - command-line version
Group:		Video
Requires: %{name} = %{version}-%{release}
Provides: avidemux-ui = %{version}-%{release}

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
%patch5 -p1
%patch6 -p1
%patch7 -p1


# libdir is nicely hardcoded
sed -i 's,Dir="lib",Dir="%{_lib}",' avidemux/main.cpp avidemux/ADM_core/src/ADM_fileio.cpp
grep -q '"%{_lib}"' avidemux/main.cpp
grep -q '"%{_lib}"' avidemux/ADM_core/src/ADM_fileio.cpp

%build
#gw 2.5.4 has linking problems in plugins/ADM_videoFilters/AvsFilter
#   	      	      	   and in plugins/ADM_videoFilters/Logo/
%define _disable_ld_no_undefined 1
%cmake
%make

# plugin build expects libraries to be already installed; we fake a prefix
# in build/ by symlinking all libraries to build/lib/
mkdir -p %_lib
cd %_lib
find ../avidemux -name '*.so*' | xargs ln -sft . 
cd ../../plugins
%cmake -DAVIDEMUX_SOURCE_DIR=%{_builddir}/%{filename} -DAVIDEMUX_CORECONFIG_DIR=%{_builddir}/%{filename}/build/config -DAVIDEMUX_INSTALL_PREFIX=%{_builddir}/%{filename}/build
make


%install
rm -rf %{buildroot}
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
Name=%{Name}
Comment=%{pkgsummary}
Exec=%{_bindir}/%{name}2_gtk %U
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=AudioVideo;Video;AudioVideoEditing;GTK;
EOF
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}-qt.desktop << EOF
[Desktop Entry]
Name=%{Name}
Comment=%{pkgsummary}
Exec=%{_bindir}/%{name}2_qt4 %U
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=AudioVideo;Video;AudioVideoEditing;Qt;
EOF

rm -rf %{buildroot}%{_datadir}/locale/klingon

%{find_lang} %{name}

%if %mdkversion <= 200710
# compatibility symlink
ln -s avidemux2_gtk %{buildroot}%{_bindir}/avidemux2
%endif

%if %mdkversion < 200900
%post gtk
%{update_menus}
%endif

%if %mdkversion < 200900
%postun gtk
%{clean_menus}
%endif

%if %mdkversion < 200900
%post qt
%{update_menus}
%endif

%if %mdkversion < 200900
%postun qt
%{clean_menus}
%endif

%clean 
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS
%if %mdkversion <= 200710
%{_bindir}/avidemux2
%endif
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
#%_libdir/ADM_plugins/audioDevices/libADM_av_arts.so
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
%if %with plf
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_faac.so
%{_libdir}/ADM_plugins/audioEncoders/libADM_ae_lame.so
%dir %{_libdir}/ADM_plugins/videoEncoder
%if %with_x264
%{_libdir}/ADM_plugins/videoEncoder/libADM_vidEnc_x264.so
%dir %{_libdir}/ADM_plugins/videoEncoder/x264/
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
%defattr(-,root,root)
%{_bindir}/avidemux2_gtk
%{_datadir}/applications/mandriva-avidemux-gtk.desktop
%{_libdir}/libADM_render_gtk.so
%{_libdir}/libADM_UIGtk.so
%if %with plf
%if %with_x264
%{_libdir}/ADM_plugins/videoEncoder/x264/libADM_vidEnc_x264_Gtk.so
%endif
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
%defattr(-,root,root)
%{_bindir}/avidemux2_qt4
%{_datadir}/applications/mandriva-avidemux-qt.desktop
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/i18n
%{_datadir}/%{name}/i18n/*.qm
%{_libdir}/libADM_render_qt4.so
%{_libdir}/libADM_UIQT4.so
%if %with plf
%if %with_x264
%{_libdir}/ADM_plugins/videoEncoder/x264/libADM_vidEnc_x264_Qt.so
%endif
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
%defattr(-,root,root)
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


%changelog
* Wed Aug 31 2011 Andrey Bondrov <abondrov@mandriva.org> 2.5.5-4plf2011.0
- Rebuild for restricted with all PLF features

* Sun Aug 28 2011 Andrey Bondrov <abondrov@mandriva.org> 2.5.5-1mdv2012.0
+ Revision: 697268
- New version: 2.5.5

  + Anssi Hannula <anssi@mandriva.org>
    - plf: append "plf" to Release on cooker to make plf build have higher EVR
      again with the rpm5-style mkrel now in use

* Mon Dec 06 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.4-2mdv2011.0
+ Revision: 612215
- fix build with new x264

* Mon Dec 06 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.4-1mdv2011.0
+ Revision: 612166
- new version
- add official patches
- enable va support
- drop patches 4,5
- fix build by disabling --no-undefined
- add avsfilter and logo filter

* Thu Sep 02 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.3-2mdv2011.0
+ Revision: 575258
- install missing libraries (bug #60877)

* Wed Sep 01 2010 Anssi Hannula <anssi@mandriva.org> 2.5.3-1mdv2011.0
+ Revision: 575026
- update file list
- fix build issues (from upstream):
  o 2.5.3_mjpeg_fix.diff
  o 2.5.3_field_asm_fix.diff
- fix underlinking issues of mpeg2enc and jack:
  o avidemux-mpeg2enc-underlinking.patch
  o avidemux-jack-underlinking.patch

  + Funda Wang <fwang@mandriva.org>
    - BR yasm
    - i18n patch not needed
    - New version 2.5.3

* Wed May 05 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.2-4mdv2010.1
+ Revision: 542369
- rebuild

* Sat Jan 23 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.2-3mdv2010.1
+ Revision: 495204
- rebuild
- reeable x264 for plf packports

* Thu Jan 14 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.2-2mdv2010.1
+ Revision: 491377
- disable x264 build on 2010.0

* Thu Jan 14 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.2-1mdv2010.1
+ Revision: 491239
- fix build on x86_64
- new source URL
- update file list

  + Funda Wang <fwang@mandriva.org>
    - new version 2.5.2

* Thu Dec 10 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.1-4mdv2010.1
+ Revision: 475968
- rebuild

* Mon Nov 09 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.1-3mdv2010.1
+ Revision: 463778
- patch for new x264

* Tue Aug 18 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.1-2mdv2010.0
+ Revision: 417570
- fix opencore detection
- remove dca plugin
- update amr build deps

* Tue Aug 18 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.1-1mdv2010.0
+ Revision: 417550
- new version
- drop patches 4,5,6,7,8
- update file list
- update deps of the GUI packages (bug #52821)
- spec cleanup, always build plugins

* Sat Jul 11 2009 Anssi Hannula <anssi@mandriva.org> 2.5.0-4mdv2010.0
+ Revision: 394818
- fix loading plugins on lib64 systems

* Fri Jul 10 2009 Anssi Hannula <anssi@mandriva.org> 2.5.0-3mdv2010.0
+ Revision: 394337
- workaround to allow building plugins before installing avidemux
- fix building plugins without lame (wrong-include.patch)
- fix underlinking (underlinking.patch)
- add missing buildrequires on libxv-devel
- make requires in UIs more strict
- drop mmx build switch, avidemux has fallbacks for non-MMX systems

* Fri Jul 10 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.0-2mdv2010.0
+ Revision: 394217
- update the patches
- support building the plugins (currently not in the mdv build)

* Fri Jul 10 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.5.0-1mdv2010.0
+ Revision: 394078
- fix installation on x86_64
- new version
- drop patches 0,2,3
- rediff patches 1,4
- fix build problems
- update file list
- fix build with new cmake

* Wed Feb 11 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.4-2mdv2009.1
+ Revision: 339350
- rebuild for new libfaad

* Tue Feb 10 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.4-1mdv2009.1
+ Revision: 339136
- new version
- drop patch 3
- fix format strings
- update patch 2
- disable arts

  + Oden Eriksson <oeriksson@mandriva.com>
    - lowercase ImageMagick

* Mon Oct 13 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.3-2mdv2009.1
+ Revision: 293213
- fix for new x264
- revert previous change
- fix x264 encoding

* Fri Jul 25 2008 Funda Wang <fwang@mandriva.org> 2.4.3-1mdv2009.0
+ Revision: 249175
- BR libxslt-proc

  + GÃ¶tz Waschk <waschk@mandriva.org>
    - fix buildrequires
    - new version
    - update build deps
    - switch to cmake
    - update file list

* Thu Jul 24 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.2-2mdv2009.0
+ Revision: 245445
- update patch 2 (libdca)

* Thu Jul 24 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.2-1mdv2009.0
+ Revision: 245406
- new version
- drop patches 3,4
- update build deps
- update libtool
- update configure options

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Sat May 31 2008 Funda Wang <fwang@mandriva.org> 2.4.1-4mdv2009.0
+ Revision: 213688
- add gentoo patches
- rebuild for new directfb

* Sun Feb 17 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.1-2mdv2008.1
+ Revision: 170042
- add qt gui and split the package

* Sun Feb 17 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.1-1mdv2008.1
+ Revision: 169979
- new version

* Thu Jan 17 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.4-2mdv2008.1
+ Revision: 154479
- rebuild

  + Thierry Vignaud <tv@mandriva.org>
    - drop old menu

* Wed Jan 02 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.4-1mdv2008.1
+ Revision: 140518
- new version

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Nov 14 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.4-0.preview3.1mdv2008.1
+ Revision: 108693
- new version

* Sat Oct 13 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.4-0.preview2.1mdv2008.1
+ Revision: 98088
- new version
- drop patch
- fix buildrequires

  + Thierry Vignaud <tv@mandriva.org>
    - kill desktop-file-validate's 'warning: key "Encoding" in group "Desktop Entry" is deprecated'

* Fri Jun 01 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 2.4-0.preview1.3mdv2008.0
+ Revision: 34310
- Rebuild with libslang2.

* Tue May 22 2007 Anssi Hannula <anssi@mandriva.org> 2.4-0.preview1.2mdv2008.0
+ Revision: 29612
- rebuild for new directfb

* Thu May 17 2007 Anssi Hannula <anssi@mandriva.org> 2.4-0.preview1.1mdv2008.0
+ Revision: 27655
- 2.4 preview 1
  o fixes loading of projects
- add cli subpackage
- add compatibility symlink for changed binary name on <= 2007.1
- update patch0


* Fri Mar 23 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.3.0-7mdv2007.1
+ Revision: 148360
- rebuild for new firefox

* Thu Mar 15 2007 Anssi Hannula <anssi@mandriva.org> 2.3.0-6mdv2007.1
+ Revision: 144509
- fix buildrequires
- better description
- use provided icons
- fix menu categories
- adapt package for Mandriva
- Import avidemux

* Tue Feb 27 2007 Götz Waschk <goetz@zarb.org> 2.3.0-5plf2007.1
- rebuild for new firefox

* Thu Feb 22 2007 Götz Waschk <goetz@zarb.org> 2.3.0-4plf2007.1
- rebuild for new libgiil

* Mon Jan 08 2007 Götz Waschk <goetz@zarb.org> 2.3.0-3plf2007.1
- rebuild for new firefox

* Thu Dec 07 2006 Götz Waschk <goetz@zarb.org> 2.3.0-2plf2007.1
- fix firefox build

* Sun Dec 03 2006 Götz Waschk <goetz@zarb.org> 2.3.0-1plf2007.1
- new version

* Fri Nov 17 2006 Anssi Hannula <anssi@zarb.org> 2.3-0.preview2.5plf2007.1
- fix firefox requires on lib64 and when backporting

* Thu Nov 09 2006 Götz Waschk <goetz@zarb.org> 2.3-0.preview2.4plf2007.1
- fix mozilla dep

* Thu Nov 09 2006 Götz Waschk <goetz@zarb.org> 2.3-0.preview2.3plf2007.1
- rebuild for new firefox

* Sun Oct 29 2006 Anssi Hannula <anssi@zarb.org> 2.3-0.preview2.2plf2007.1
- disable parallel build

* Fri Oct 20 2006 Götz Waschk <goetz@zarb.org> 2.3-0.preview2.1plf2007.1
- drop the patch
- new version

* Thu Oct 19 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.10plf2007.1
- rebuild

* Tue Sep 19 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.9plf2007.0
- rebuild

* Mon Sep 18 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.8plf2007.0
- rebuild for new firefox

* Sat Sep 09 2006 Anssi Hannula <anssi@zarb.org> 2.2.0-0.preview2b.7plf2007.0
- fix LDFLAGS for lib64 on backports

* Sat Sep 09 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.6plf2007.0
- don't apply the patch on 2006.0

* Wed Aug 30 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.5plf2007.0
- patch for new x264

* Fri Aug 04 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.4plf2007.0
- rebuild for new firefox

* Tue Aug 01 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.3plf2007.0
- Rebuild for new firefox

* Sun Jul 02 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.2plf2007.0
- rebuild

* Fri Jun 23 2006 Götz Waschk <goetz@zarb.org> 2.2.0-0.preview2b.1plf2007.0
- add xdg menu
- new version

* Sun Jun 04 2006 Götz Waschk <goetz@zarb.org> 2.1.2-5plf2007.0
- Rebuild for new firefox

* Thu May 04 2006 GÃ¶tz Waschk <goetz@zarb.org> 2.1.2-4plf
- rebuild for new firefox

* Sat Apr 22 2006 Götz Waschk <goetz@zarb.org> 2.1.2-3plf
- rebuild for new firefox

* Thu Apr 06 2006 Götz Waschk <goetz@zarb.org> 2.1.2-2plf
- rebuild to fix firefox dep

* Wed Mar 08 2006 Götz Waschk <goetz@zarb.org> 2.1.2-1plf
- drop patch

* Wed Mar 08 2006 GÃ¶tz Waschk <goetz@zarb.org> 2.1.2-1plf
- New release 2.1.2

* Fri Feb 03 2006 GÃ¶tz Waschk <goetz@zarb.org> 2.1.0-3plf
- rebuild for new mozilla-firefox

* Tue Jan 10 2006 GÃ¶tz Waschk <goetz@zarb.org> 2.1.0-2plf
- rebuild  for new mozilla-firefox

* Tue Dec 27 2005 Götz Waschk <goetz@zarb.org> 2.1.0-1plf
- new version

* Thu Oct 27 2005 Götz Waschk <goetz@zarb.org> 2.1.0-0.step3.2plf
- rebuild for new firefox

* Thu Oct 20 2005 Götz Waschk <goetz@zarb.org> 2.1.0-0.step3.1plf
- new version

* Tue Sep 27 2005 Goetz Waschk <goetz@ryu.zarb.org> 2.1.0-0.step2.2plf
- add rpath to fix mozilla linking

* Tue Sep 13 2005 Götz Waschk <goetz@zarb.org> 2.1.0-0.step2.1plf
- enable x264
- rediff the patch
- new version

* Wed Aug 17 2005 Götz Waschk <goetz@zarb.org> 2.1-0.step1.1plf
- bump deps
- drop source 4
- new version

* Thu Jun 16 2005 Götz Waschk <goetz@zarb.org> 2.0.40-1plf
- ugly workaround for Cooker's broken gcc4
- new version

* Wed May 04 2005 Götz Waschk <goetz@zarb.org> 2.0.38-0.rc3.1plf
- new version

* Wed Apr 20 2005 Götz Waschk <goetz@zarb.org> 2.0.38-0.rc2b.2plf
- mkrel macro

* Sat Apr 02 2005 Götz Waschk <goetz@zarb.org> 2.0.38-0.rc2b.1plf
- decompress icons
- update buildrequires
- enable mmx (doesn't build otherwise)
- new version

* Fri Apr 01 2005 Götz Waschk <goetz@zarb.org> 2.0.38-0.rc1.1plf
- New release 2.0.38rc1

* Thu Feb 17 2005 Götz Waschk <goetz@zarb.org> 2.0.36-1plf
- new version

* Mon Dec 06 2004 Laurent Culioli <laurent@zarb.org> 2.0.34-0.test1.1plf
- 2.0.34-test1
- Drop Patch0

* Wed Oct 27 2004 Laurent Culioli <laurent@zarb.org> 2.0.32-1plf
- 2.0.32
- Patch0: mpeg ps fix.

* Sat Aug 14 2004 Götz Waschk <goetz@zarb.org> 2.0.28-1plf
- source URL
- New release 2.0.28

* Sat Jul 24 2004 Götz Waschk <goetz@plf.zarb.org> 2.0.26-1plf
- update buildrequires
- reenable libtoolize on cooker
- New release 2.0.26

* Mon May 10 2004 Götz Waschk <goetz@plf.zarb.org> 2.0.24-1plf
- add source url
- New release 2.0.24

* Thu Apr 15 2004 Götz Waschk <goetz@plf.zarb.org> 2.0.22-1plf
- don't run libtoolize
- update description
- drop merged patch
- fix buildrequires
- new version

