for dir in ./schema/*/     # list of uservices repositories
do
    dir=${dir%*/}       # remove the trailing "/"
    dir_name=${dir##*/} # everything after the final "/"
    echo "${dir_name}"
    twine upload -u admin -p secret123 --repository-url http://localhost:8081/repository/onlexnet/ python/$dir_name/dist/*
done

# publish additional (not based on avro/grpc schemas) projects
twine upload -u admin -p secret123 --repository-url http://localhost:8081/repository/onlexnet/ python/onlexnet/dist/*
