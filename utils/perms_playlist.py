from guardian.shortcuts import (get_perms,
                                assign_perm,
                                remove_perm)


def get_playlist_perms_obj(user, playlist_obj):
    return PlaylistPerms(user=user, playlist_object=playlist_obj)


def get_basic_perms():
    return [
        'get_playlist',
        'add_music',
        'remove_music'
    ]


def get_admin_perms():
    return [
        'get_playlist',
        'add_music',
        'remove_music',
        'change_playlist',
        'delete_playlist',
        'view_playlist_perms',
        'set_playlist_perms',
        'remove_playlist_perms',
        'all_playlist_perms',
    ]


class PlaylistPerms:
    def __init__(self, user, playlist_object):
        self.user = user
        self.playlist_object = playlist_object

    def get_user_perms(self):
        return get_perms(self.user, self.playlist_object)

    def get_user(self):
        return self.user

    def get_playlist(self):
        if not self.playlist_object.private:
            return self.playlist_object
        if self.check_perms('get_playlist'):
            return self.playlist_object

        return None

    def get_playlist_user(self):
        return self.playlist_object.user

    def set_basic_perms(self):
        """
           Sets basic permissions for a playlist:
           - 'get_playlist': view playlist object.
           - 'add_music': adding music to playlist.
           - 'remove_music': removing music from playlist.
        """

        self.add_perms(get_basic_perms())

    def set_admin_perms(self):
        """
            Sets admin permissions for a playlist:
            - 'get_playlist': view playlist object.
            - 'add_music': adding music to playlist.
            - 'remove_music': removing music from playlist.
            - 'change_playlist': changing playlist object.
            - 'delete_playlist': deleting playlist object.
            - 'all_playlist_perms': global permissions for all playlist.
        """

        self.add_perms(get_admin_perms())

    def add_perm(self, perm):
        if perm == "all_playlist_perms":
            print("Permission Denied!!!")
            return
        assign_perm(perm, self.user, self.playlist_object)

    def add_perms(self, perms):
        for perm in perms:
            if perm == "all_playlist_perms":
                print("Permission Denied!!!")
                continue
            assign_perm(perm, self.user, self.playlist_object)

    def check_perms(self, perm):
        # Если у пользователя есть глобальное право, разрешить всё
        if 'all_playlist_perms' in get_perms(self.user, self.playlist_object):
            return True
        # Иначе проверяем конкретное право
        return perm in get_perms(self.user, self.playlist_object)

    def remove_perms(self, perm):
        """
            Deletes permissions for a playlist
        """
        remove_perm(perm, self.user, self.playlist_object)

    def remove_perm_list(self, perms):
        """
            Removes permissions for a playlist
        """

        for perm in perms:
            remove_perm(perm, self.user, self.playlist_object)

    def reset_perms(self):
        """
            Resets permissions for a playlist
        """

        for perm in get_perms(self.user, self.playlist_object):
            self.remove_perms(perm)
