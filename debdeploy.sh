set -ex

TARGET="$1"

[ -n "$TARGET" ]

PACKAGE="$(dpkg-parsechangelog | sed -n 's/Source: //p')"
VERSION="$(dpkg-parsechangelog | sed -n 's/Version: //p')"

DEB="${PACKAGE}_${VERSION}_all.deb"

TEMP="$(mktemp -d)"
trap "rm -r $TEMP" EXIT

rsync -a --exclude .svn . "$TEMP/$PACKAGE"
cd "$TEMP/$PACKAGE"
debuild -us -uc
scp ../$DEB "$TARGET":
ssh "$TARGET" sudo dpkg -i "$DEB"
cd -
