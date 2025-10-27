#!/bin/sh

ECHO=`which echo`

DIFF_FLAGS="-u"

tests_succeeded=0
tests_total=0
for file in ./*.yaml ; do
    file_short=`basename $file`
    test_name=`echo $file_short | sed -e 's/\.yaml//'`

    ${ECHO} -n " test ($test_name): "
    success="SUCCESS"
    check-jsonschema --schemafile ../schema/metadata.json $file > ${file}.test
    diff ${DIFF_FLAGS} ${file}.gold ${file}.test > ${file}.out
    if [ $? -eq 0 ] ; then
        tests_succeeded=$(( $tests_succeeded + 1 ))
    else
        success="FAILURE"
        ${ECHO}
        cat ${file}.out
    fi
    rm ${file}.test ${file}.out

    ${ECHO} $success
    tests_total=$(( tests_total + 1 ))
done

${ECHO} $tests_succeeded/$tests_total tests successful
