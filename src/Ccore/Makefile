SRCS := nav_alg.cpp
OBJS := ${SRCS:cpp=o}
BIN = libnav.so

CC = g++
CPPFLAGS=-std=c++17 -Wall -Werror -Wpedantic -fpic
LDFLAGS=-shared -Wl,-soname

.PHONY: all
all: ${BIN}

$(BIN): $(OBJS)
	${CC} ${LDFLAGS},$@ $< -o $@

%.o: %.cpp
	${CC} -c ${CPPFLAGS} $<

clean_obj:
	rm -f ${OBJS}

clean_bin:
	rm -f ${BIN}

clean: clean_obj clean_bin
	@echo "all clean"