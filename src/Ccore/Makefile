LIB_SRCS := \
		src/nav_alg.cpp
API_SRCS := \
		src/analysis_api.cpp
TEST_SRC := \
		test/test.cpp

LIB_OBJS := ${LIB_SRCS:cpp=o}
API_OBJS := ${API_SRCS:cpp=o}

HDRS := include
LIB = lib/libnav.so
API = lib/libnavapi.so

TEST_BIN = test.out

CC = g++
CPPFLAGS=-std=c++17 -Wall -Werror -Wpedantic -fpic -O0
LINKAGE=-shared

LDFLAGS=navapi
LDPATH=lib/

.PHONY: all api lib clean
all: api
lib: ${LIB}
api: ${API}

$(LIB): $(LIB_OBJS)
	${CC} ${LINKAGE} $< -o $@

$(API): ${LIB_OBJS} ${API_OBJS}
	${CC} ${LINKAGE} $^ -o $@

test_dynamic: ${TEST_SRC} ${API}
	${CC} -ggdb -L${LDPATH} ${CPPFLAGS} $(addprefix -I,$(HDRS)) -l${LDFLAGS} ${TEST_SRC} -o ${TEST_BIN}

test_static: ${TEST_SRC} ${API_SRCS} ${LIB_SRCS}
	${CC} -ggdb ${CPPFLAGS} $(addprefix -I,$(HDRS)) $^ -o ${TEST_BIN}

%.o: %.cpp
	${CC} -c $(addprefix -I,$(HDRS)) ${CPPFLAGS} $< -o $@

clean_lib:
	rm -f ${LIB} ${LIB_OBJS}
clean_api:
	rm -f ${API} ${API_OBJS}
clean_test:
	rm -f ${TEST_BIN}
clean: clean_lib clean_api clean_test
	@echo "all clean"