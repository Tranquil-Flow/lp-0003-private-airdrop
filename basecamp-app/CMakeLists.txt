cmake_minimum_required(VERSION 3.20)
project(lp0003_private_airdrop_basecamp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 COMPONENTS Core Quick QuickWidgets Widgets QUIET)

if(Qt6_FOUND)
  qt_add_resources(LP0003_QRC resources.qrc)
  add_library(lp0003_private_airdrop MODULE
    src/Lp0003Component.cpp
    src/Lp0003Component.h
    include/IComponent.h
    ${LP0003_QRC}
  )
  target_include_directories(lp0003_private_airdrop PRIVATE include src)
  target_link_libraries(lp0003_private_airdrop PRIVATE Qt6::Core Qt6::Quick Qt6::QuickWidgets Qt6::Widgets)
else()
  message(WARNING "Qt6 not found; source package can still be inspected and packaged as .lgx, but native build/load evidence remains pending.")
endif()
