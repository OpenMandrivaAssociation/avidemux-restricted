%define filename %{name}_%{version}
######################
# to build ths need to add non-free, contrib,main, and restricted at the build time.
#############################
# Hardcore PLF build
# bcond_with or bcond_without
%bcond_without plf
#############################
%define         ffmpeg_version 1.2.6

%if %with plf
%define distsuffix plf
# make EVR of plf build higher than regular to allow update, needed with rpm5 mkrel
%define extrarelsuffix plf
%endif

Name:		avidemux
Version:	2.6.8
Release:	1%{?extrarelsuffix}
Summary:	A free video editor
License:	GPLv2+
Group:		Video
Url:		http://fixounet.free.fr/avidemux
Source0:	http://downloads.sourceforge.net/project/%{name}/%{name}/%{version}/%{filename}.tar.gz
Source3:        ffmpeg-%{ffmpeg_version}.tar.bz2
Source4:        xvba_support_from_xbmc_xvba.patch
Source100:	%{name}.rpmlintrc

Patch0:         avidemux-cmake-2.8.8.patch
Patch1:         avidemux-linking.patch
Patch2:         avidemux-x264_plugins.patch
Patch3:         avidemux-package_version.patch

BuildRequires:	cmake
BuildRequires:	imagemagick
BuildRequires:	libxslt-proc
BuildRequires:	nasm
BuildRequires:	qt4-linguist
BuildRequires:	yasm yasm-devel
BuildRequires:	gettext-devel
BuildRequires:  intltool
BuildRequires:  dos2unix
BuildRequires:  pkgconfig(sqlite)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(mozjs185)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(samplerate)
BuildRequires:	qt4-devel
BuildRequires:	pkgconfig(gdk-3.0)
BuildRequires:	pkgconfig(esound)
BuildRequires:	pkgconfig(jack)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(libass)
BuildRequires:	pkgconfig(libva)
BuildRequires:	pkgconfig(mad)
BuildRequires:	pkgconfig(sdl)
BuildRequires:	pkgconfig(vorbis)
BuildRequires:	pkgconfig(xv)
BuildRequires:  pkgconfig(xmu)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glu)
BuildRequires:  pkgconfig(vdpau)
BuildRequires:  a52dec-devel
BuildRequires:  pkgconfig(libdca)
BuildRequires:  pkgconfig(vpx)
BuildRequires:  pkgconfig(twolame)
BuildRequires:  aften-devel
BuildRequires:  pkgconfig(dcaenc)
BuildRequires:  pkgconfig(cairo)
%if %with plf
BuildRequires:	libfaac-devel
BuildRequires:	libfaad2-devel
BuildRequires:	liblame-devel
BuildRequires:	xvid-devel
BuildRequires:	pkgconfig(opencore-amrnb)
BuildRequires:	pkgconfig(opencore-amrwb)
BuildRequires:	pkgconfig(x264)
%endif
Requires:	avidemux-ui = %{version}-%{release}

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
Requires:	gtk+3.0 >= 3.8.6
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
%setup -qn %{filename}
# convert docs
find . -type f -exec dos2unix -q {} \;
# replace old ffmpeg and build it for the core.
sed -i -e 's|set(FFMPEG_VERSION "1.2.1")|set(FFMPEG_VERSION "%{ffmpeg_version}")|g' cmake/admFFmpegBuild.cmake
rm -f avidemux_core/ffmpeg_package/ffmpeg-1.2.1.tar.bz2
cp %{S:3} avidemux_core/ffmpeg_package/
pushd avidemux_core/ffmpeg_package/patches/xvba
rm -f xvba_support_from_xbmc_xvba.patch
cp %{S:4} .
popd
# fix some linting
find . -type f -exec chmod -x {} \;

#  paches
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0

%build
export CXXFLAGS="%{optflags} -fno-strict-aliasing"

chmod 755 bootStrap.bash
./bootStrap.bash --with-cli --with-gtk

%install
cp -r install/* %{buildroot}

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
Exec=%{_bindir}/%{name}3_gtk %U
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
Exec=%{_bindir}/%{name}3_qt4 %U
Icon=%{name}
Terminal=false
Type=Application
StartupNotify=true
Categories=AudioVideo;Video;AudioVideoEditing;Qt;
EOF

# Install man
install -D -m644 man/avidemux.1 %{buildroot}%{_mandir}/man1/avidemux.1

# delete devel file (only needed for build)
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_datadir}/locale/klingon

#find_lang %{name}

#files -f %{name}.lang
%files
%doc AUTHORS COPYING README
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
# man
%{_mandir}/man1/avidemux.1.*
# TODO: maybe split help and lang packages.
# lang
%dir %{_datadir}/avidemux3
%{_datadir}/avidemux3/help/
# help files
%{_datadir}/avidemux3/i18n/
#
%{_libdir}/libADM6postproc.so.52
%{_libdir}/libADM6avcodec.so.54
%{_libdir}/libADM6avformat.so.54
%{_libdir}/libADM6avutil.so.52
%{_libdir}/libADM6swscale.so.2
%{_libdir}/libADM_audioParser6.so
%{_libdir}/libADM_core6.so
%{_libdir}/libADM_coreAudio6.so
%{_libdir}/libADM_coreAudioDevice6.so
%{_libdir}/libADM_coreAudioEncoder6.so
%{_libdir}/libADM_coreAudioFilterAPI6.so
%{_libdir}/libADM_coreDemuxer6.so
%{_libdir}/libADM_coreDemuxerMpeg6.so
%{_libdir}/libADM_coreImage6.so
%{_libdir}/libADM_coreImageLoader6.so
%{_libdir}/libADM_coreJobs.so
%{_libdir}/libADM_coreLibVA6.so
%{_libdir}/libADM_coreMuxer6.so
%{_libdir}/libADM_coreScript.so
%{_libdir}/libADM_coreSocket6.so
%{_libdir}/libADM_coreSqlLight3.so
%{_libdir}/libADM_coreSubtitle.so
%{_libdir}/libADM_coreUI6.so
%{_libdir}/libADM_coreUtils6.so
%{_libdir}/libADM_coreVDPAU6.so
%{_libdir}/libADM_coreVideoCodec6.so
%{_libdir}/libADM_coreVideoEncoder6.so
%{_libdir}/libADM_coreVideoFilter6.so
%dir %{_libdir}/ADM_plugins6
%dir %{_libdir}/ADM_plugins6/audioDecoder
%dir %{_libdir}/ADM_plugins6/audioDevices
%dir %{_libdir}/ADM_plugins6/audioEncoders
%dir %{_libdir}/ADM_plugins6/autoScripts
%dir %{_libdir}/ADM_plugins6/autoScripts/lib
%dir %{_libdir}/ADM_plugins6/demuxers
%dir %{_libdir}/ADM_plugins6/muxers
%dir %{_libdir}/ADM_plugins6/pluginSettings
%dir %{_libdir}/ADM_plugins6/scriptEngines
%dir %{_libdir}/ADM_plugins6/videoDecoders
%dir %{_libdir}/ADM_plugins6/videoEncoders
%dir %{_libdir}/ADM_plugins6/videoFilters
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_a52.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_dca.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_faad.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_ima_adpcm.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_lav.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_Mad.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_ms_adpcm.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_ulaw.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_vorbis.so
%{_libdir}/ADM_plugins6/audioDevices/libADM_av_alsaDefault.so
%{_libdir}/ADM_plugins6/audioDevices/libADM_av_alsaDMix.so
%{_libdir}/ADM_plugins6/audioDevices/libADM_av_alsaHw.so
%{_libdir}/ADM_plugins6/audioDevices/libADM_av_esd.so
%{_libdir}/ADM_plugins6/audioDevices/libADM_av_jack.so
%{_libdir}/ADM_plugins6/audioDevices/libADM_av_oss.so
%{_libdir}/ADM_plugins6/audioDevices/libADM_av_pulseAudioSimple.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_aften.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_dcaenc.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_lav_ac3.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_lav_mp2.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_pcm.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_twolame.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_vorbis.so
%{_libdir}/ADM_plugins6/autoScripts/720p.py
%{_libdir}/ADM_plugins6/autoScripts/check24fps.py
%{_libdir}/ADM_plugins6/autoScripts/dvd.py
%{_libdir}/ADM_plugins6/autoScripts/lib/ADM_image.py
%{_libdir}/ADM_plugins6/autoScripts/lib/ADM_imageInfo.py
%{_libdir}/ADM_plugins6/autoScripts/PSP.py
%{_libdir}/ADM_plugins6/autoScripts/svcd.py
%{_libdir}/ADM_plugins6/autoScripts/vcd.py
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_asf.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_avsproxy.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_flv.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_matroska.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_mp4.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_mxf.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_opendml.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_pic.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_ps.so
%{_libdir}/ADM_plugins6/demuxers/libADM_dm_ts.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_avi.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_dummy.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_ffPS.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_ffTS.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_flv.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_Mkv.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_mp4.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_mp4v2.so
%{_libdir}/ADM_plugins6/muxers/libADM_mx_raw.so
%{_libdir}/ADM_plugins6/scriptEngines/libADM_script_qt.so
%{_libdir}/ADM_plugins6/scriptEngines/libADM_script_spiderMonkey.so
%{_libdir}/ADM_plugins6/scriptEngines/libADM_script_tinyPy.so
%{_libdir}/ADM_plugins6/videoDecoders/libADM_vd_vpx.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_ffDv.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_ffFlv1.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_ffMpeg2.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_ffMpeg4.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_huff.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_jpeg.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_null.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_png.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_yv12.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_hf_hflip.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_addBorders.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_avsfilter.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_blackenBorders.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_changeFps.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_colorYuv.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_decimate.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_denoise3d.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_denoise3dhq.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_DgBob.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_dummy.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_fadeToBlack.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_FluxSmooth.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_gauss.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_hzstackField.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_kernelDeint.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_largeMedian.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_lavDeint.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_logo.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_lumaOnly.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_mean.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_median.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_mergeField.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_msharpen.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_printInfo.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_removePlane.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_resampleFps.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_rotate.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_separateField.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_sharpen.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_ssa.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_stackField.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_swapUV.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_telecide.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_unstackField.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_vdpauFilter.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_vdpauFilterDeint.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_vflip.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_yadif.so
%dir %{_datadir}/ADM6_addons
%dir %{_datadir}/ADM6_addons/avsfilter
%{_datadir}/ADM6_addons/avsfilter/avsload.exe
%{_datadir}/ADM6_addons/avsfilter/pipe_source.dll

#
%if %with plf
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_faac.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_lame.so
%{_libdir}/ADM_plugins6/audioEncoders/libADM_ae_lav_aac.so
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_xvid4.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_opencore_amrnb.so
%{_libdir}/ADM_plugins6/audioDecoder/libADM_ad_opencore_amrwb.so
%dir %{_libdir}/ADM_plugins6/pluginSettings/x264
%dir %{_libdir}/ADM_plugins6/pluginSettings/x264/3
%{_libdir}/ADM_plugins6/pluginSettings/x264/3/ultraFast.json
%{_libdir}/ADM_plugins6/pluginSettings/x264/3/PSP.json
%{_libdir}/ADM_plugins6/pluginSettings/x264/3/veryFast.json
%{_libdir}/ADM_plugins6/pluginSettings/x264/3/fast.json
%{_libdir}/ADM_plugins6/pluginSettings/x264/3/iPhone.json
%endif

%files gtk
%doc AUTHORS COPYING README
%{_datadir}/applications/mandriva-avidemux-gtk.desktop
%{_bindir}/avidemux3_gtk
%{_libdir}/libADM_render6_gtk.so
%{_libdir}/libADM_toolkitGtk.so
%{_libdir}/libADM_UIGtk6.so
%dir %{_libdir}/ADM_glade
%dir %{_libdir}/ADM_glade/main
%dir %{_libdir}/ADM_glade/videoFilter
%{_libdir}/ADM_glade/about.gtkBuilder
%{_libdir}/ADM_glade/avidemux_icon.png
%{_libdir}/ADM_glade/calculator.gtkBuilder
%{_libdir}/ADM_glade/DIA_alternate.gtkBuilder
%{_libdir}/ADM_glade/encoding.gtkBuilder
%{_libdir}/ADM_glade/main/avidemux_icon_small.png
%{_libdir}/ADM_glade/main/first-frame.png
%{_libdir}/ADM_glade/main/gtk2_build.gtkBuilder
%{_libdir}/ADM_glade/main/last-frame.png
%{_libdir}/ADM_glade/main/markA.png
%{_libdir}/ADM_glade/main/markB.png
%{_libdir}/ADM_glade/main/next-black-frame.png
%{_libdir}/ADM_glade/main/next-frame.png
%{_libdir}/ADM_glade/main/next-key-frame.png
%{_libdir}/ADM_glade/main/play.png
%{_libdir}/ADM_glade/main/previous-black-frame.png
%{_libdir}/ADM_glade/main/previous-frame.png
%{_libdir}/ADM_glade/main/previous-key-frame.png
%{_libdir}/ADM_glade/main/stop.png
%{_libdir}/ADM_glade/properties.gtkBuilder
%{_libdir}/ADM_glade/videoFilter/1.png
%{_libdir}/ADM_glade/videoFilter/2.png
%{_libdir}/ADM_glade/videoFilter/3.png
%{_libdir}/ADM_glade/videoFilter/4.png
%{_libdir}/ADM_glade/videoFilter/5.png
%{_libdir}/ADM_glade/videoFilter/6.png
%{_libdir}/ADM_glade/videoFilter/7.png
%{_libdir}/ADM_glade/videoFilter/add.png
%{_libdir}/ADM_glade/videoFilter/cd.png
%{_libdir}/ADM_glade/videoFilter/close.png
%{_libdir}/ADM_glade/videoFilter/down.png
%{_libdir}/ADM_glade/videoFilter/exec.png
%{_libdir}/ADM_glade/videoFilter/fileopen.png
%{_libdir}/ADM_glade/videoFilter/filesave.png
%{_libdir}/ADM_glade/videoFilter/filesaveas.png
%{_libdir}/ADM_glade/videoFilter/gl.png
%{_libdir}/ADM_glade/videoFilter/remove.png
%{_libdir}/ADM_glade/videoFilter/thumbnail.png
%{_libdir}/ADM_glade/videoFilter/up.png
%{_libdir}/ADM_glade/videoFilter/videoFilter.gtkBuilder
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_asharpGtk.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_chromaShiftGtk.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_contrastGtk.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_cropGtk.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_eq2Gtk.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_HueGtk.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_swscaleResize_gtk.so
%if %with plf
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_x264_gtk.so
%endif


%files qt
%doc AUTHORS COPYING README
%{_datadir}/applications/mandriva-avidemux-qt.desktop
%{_bindir}/avidemux3_jobs
%{_bindir}/avidemux3_qt4
%{_libdir}/libADM_render6_qt4.so
%{_libdir}/libADM_UIQT46.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_asharpQt4.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_chromaShiftQt4.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_contrastQt4.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_cropQt4.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_eq2Qt4.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_glBenchmark.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_glResize.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_HueQt4.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_mpdelogoQt4.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_rotateGlFrag2.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_sampleGlFrag2.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_sampleGlVertex.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_swscaleResize_qt4.so
%if %with plf
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_x264_qt4.so
%endif

%files cli
%doc README
%{_bindir}/avidemux3_cli
%{_libdir}/libADM_render6_cli.so
%{_libdir}/libADM_UI_Cli6.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_chromaShiftCli.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_contrastCli.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_CropCli.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_eq2Cli.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_HueCli.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_mpdelogoCli.so
%{_libdir}/ADM_plugins6/videoFilters/libADM_vf_swscaleResize_cli.so
%if %with plf
%{_libdir}/ADM_plugins6/videoEncoders/libADM_ve_x264_cli.so
%endif