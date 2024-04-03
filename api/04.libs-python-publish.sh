devpi use http://localhost:3141
devpi login root --password=
devpi index -c dev bases=root/pypi
devpi use root/dev

export TWINE_PASSWORD=
for dir in ./schema/*/     # list of uservices repositories
do
    dir=${dir%*/}       # remove the trailing "/"
    dir_name=${dir##*/} # everything after the final "/"
    echo "${dir_name}"
    twine upload -u root --repository-url http://localhost:3141/root/dev python/$dir_name/dist/*
done

# publish additional (not based on avro/grpc schemas) projects
twine upload -u root --repository-url http://localhost:3141/root/dev python/onlexnet/dist/*
