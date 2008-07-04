function regenerate(form) {
    var requiredLength = 6
    var allowedCharacters="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    var new_access=""
    for (i = 1; i <= requiredLength; i++)
    {
        var idxChar=Math.floor(Math.random()*(allowedCharacters.length))
        new_access = new_access + allowedCharacters[idxChar]
    }
    form.ACCESS_KEY.value = new_access
}
