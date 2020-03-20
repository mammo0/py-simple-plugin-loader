import setuptools

# gitpython is needed for version tagging
setuptools._install_setup_requires({"setup_requires": "gitpython"})
import git  #noqa


# get the description from README.md
with open("README.md", 'r') as readme:
    long_description = readme.read()


# get the version from git
def get_version():
    repo = git.Repo(search_parent_directories=True)

    if repo.tags:
        # get the latest tag
        latest_tag = sorted(repo.tags, key=lambda t: t.commit.committed_date, reverse=True)[0]
        # check if the latest commit is a release
        if repo.head.commit.hexsha == latest_tag.commit.hexsha:
            # just return the release tag
            return latest_tag.name
        else:
            # get amount of commits since the last tag as pre-release
            commit_count_since_latest_tag = len(list(repo.iter_commits(max_age=latest_tag.commit.authored_date))) - 1
            # return a pre-release tag
            return "%s.post%s" % (latest_tag.name, commit_count_since_latest_tag)
    else:
        # get the current commit count to use as pre-release
        git_commit_count = len(list(repo.iter_commits()))
        # default 'no-release' tag
        return "0.0a%s" % git_commit_count


# the actual setup
setuptools.setup(
    name="simple-plugin-loader",
    version=get_version(),
    author="Marc Ammon",
    author_email="marc.ammon@hotmail.de",
    description="Dynamically load other python modules to your project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mammo0/py-simple-plugin-loader",
    packages=["simple_plugin_loader"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
