const r = require('./renren/js/encrypt')


function getKeys(e, n, maxdigits) {
    r.getKeys(e, n, maxdigits)
}

function encrypt(e,n,maxdigits,pass) {
    r.getKeys(e, n, maxdigits)
    return r.encrypt(pass)
}