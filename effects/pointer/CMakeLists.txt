cmake_minimum_required(VERSION 3.20)
project(ScarletPointer VERSION 1.0.2 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
find_package(ECM 6.0 REQUIRED NO_MODULE)
list(APPEND CMAKE_MODULE_PATH ${ECM_MODULE_PATH})
# ECM must know the Qt major version before any KDE install/settings modules run.
# Otherwise ECM's compatibility default can query Qt5 qmake on a Qt6 desktop.
set(QT_MAJOR_VERSION 6)
find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets DBus Quick)
include(KDEInstallDirs6)
include(KDECMakeSettings)
find_package(KF6 REQUIRED COMPONENTS Config CoreAddons KCMUtils)
find_package(KWin 6.3 REQUIRED CONFIG)

kcoreaddons_add_plugin(scarletpointer SOURCES src/effect.cpp src/settings.cpp src/motion.cpp src/art.cpp
    INSTALL_NAMESPACE "kwin/effects/plugins")
target_link_libraries(scarletpointer PRIVATE KWin::kwin Qt6::Gui KF6::ConfigCore KF6::ConfigGui KF6::CoreAddons)
if(KWin_VERSION VERSION_LESS "6.7")
    target_compile_definitions(scarletpointer PRIVATE SCARLET_RENDERER_FACTORY)
endif()
kcoreaddons_add_plugin(scarletpointer_config SOURCES src/config.cpp src/settings.cpp src/motion.cpp src/art.cpp
    INSTALL_NAMESPACE "kwin/effects/configs")
target_link_libraries(scarletpointer_config PRIVATE KF6::KCMUtils KF6::ConfigCore KF6::ConfigGui KF6::CoreAddons Qt6::Widgets Qt6::DBus)
message(STATUS "Scarlet Pointer will use the KWin ${KWin_VERSION} plugin ABI")
