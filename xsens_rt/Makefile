XSENS_INSTALL_PREFIX?=$(shell dirname $$(pwd))/modules/xsens
LIBNAV_INSTALL_PREFIX?=$(shell dirname $$(pwd))/modules/libnav
GNUPLOT_INSTALL_PREIFX?=$(shell dirname $$(pwd))/modules/gnuplot-iostream
SRCS := \
		src/callbackHandler.cpp \
		src/Xsens.cpp \
		src/pyInterface.cpp \

TEST_SRC := src/main.cpp

OBJS := ${SRCS:cpp=o}
TEST_OBJS := ${TEST_SRC:cpp=o}

HDRS := include
INCLUDE := $(XSENS_INSTALL_PREFIX)/include \
           $(XSENS_INSTALL_PREFIX)/include/xsensdeviceapi \
		   $(LIBNAV_INSTALL_PREFIX)/include \
		   $(GNUPLOT_INSTALL_PREIFX)

LFLAGS:=-lm -lxsensdeviceapi -lxstypes -lpthread -lnav -lxsens \
	-L$(XSENS_INSTALL_PREFIX)/lib -Wl,-rpath,$(XSENS_INSTALL_PREFIX)/lib \
	-L$(LIBNAV_INSTALL_PREFIX)/lib -Wl,-rpath,$(LIBNAV_INSTALL_PREFIX)/lib \
	-Llib -Wl,-rpath,lib \

#LFLAGS+=-lutil -lboost_iostreams -lboost_system -lboost_filesystem
LFLAGS+=`root-config --glibs`

LIB = lib/libxsens.so
TEST = test
CC = g++

CPPFLAGS=-g -ggdb -O0 -fPIC -Wall -Wextra -Werror `root-config --cflags`
LINKAGE=-shared

.PHONY: all lib
all: lib
lib: ${LIB}
test: $(TEST)

%.o:%.cpp
	${CC} $(addprefix -I,$(HDRS)) $(addprefix -I,$(INCLUDE)) ${CPPFLAGS} -c $< -o $@

$(LIB): $(OBJS)
	${CC} ${LINKAGE} $^ -o $@

$(TEST): $(LIB) $(TEST_OBJS)
	${CC} $(addprefix -I,$(HDRS)) $(CPPFLAGS) $(TEST_OBJS) -o $@ $(LFLAGS)

echo: $(XSENS_INSTALL_PREFIX)
	@echo $<

clean_lib:
	rm -f ${LIB} ${OBJS}
clean: clean_lib
	rm -f $(TEST)
	rm -f ${TEST_OBJS}
	@echo "all clean"