from Crypto.Hash import SHA512
from Crypto.Util import number


AUTH_PUBLIC_KEY_N = 138629102600926243670082740923812406165102477170257116330086261105182415341299071043517703787021087669201982510307753420243968626630413232274952270664709568257353412890422180280652106262508962933700578008755312582990740343605756678151336383385092315873326768792062950797996222137353307053392564860072238123223

AUTH_PUBLIC_KEY_E = 65537

AUTH_PUBLIC_KEY_D = 35113647301148597661219974965825197099969499992771535637570104434838764280720273728159572193792057239555562654242774414087460201139277959866399250698600461422713156853556141667944933868036503097250086259006926979119504504598362872447156244183560794325858361366573965449134058365289067005307860927088206985473

def get_blinded_secret(secret, seed = 45):
    hashed_secret = int(SHA512.new(secret.encode('utf-8')).hexdigest(), 16)
    print (hashed_secret)
    r = seed
    while number.GCD(seed, AUTH_PUBLIC_KEY_N) != 1:
        r += 1
    blinded_secret = ((r ** AUTH_PUBLIC_KEY_E) * hashed_secret) % AUTH_PUBLIC_KEY_N

    return hex(blinded_secret)

def get_signed_blinded_secret(secret):
    signed_blinded_secret = pow(int(secret, 16), AUTH_PUBLIC_KEY_D, AUTH_PUBLIC_KEY_N)
    return hex(signed_blinded_secret)

def get_unblinded_secret(secret, seed = 45):
    r = seed
    while number.GCD(seed, AUTH_PUBLIC_KEY_N) != 1:
        r += 1
    assert number.GCD(r, AUTH_PUBLIC_KEY_N) == 1
    r_inv = number.inverse(r, AUTH_PUBLIC_KEY_N)
    assert r * r_inv % AUTH_PUBLIC_KEY_N == 1
    unblinded_secret = (r_inv * int(secret, 16)) % AUTH_PUBLIC_KEY_N

    return hex(unblinded_secret)

def verify_signature(secret, signature):
    hashed_secret = int(SHA512.new(secret.encode('utf-8')).hexdigest(), 16)
    hashed_secret_signature = pow(hashed_secret, AUTH_PUBLIC_KEY_D, AUTH_PUBLIC_KEY_N)
    return int(signature, 16) == hashed_secret_signature
