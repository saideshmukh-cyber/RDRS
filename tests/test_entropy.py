from app.core.entropy import shannon_entropy

def test_empty_entropy(): assert shannon_entropy(b"")==0.0

def test_repeated_bytes_low_entropy(): assert shannon_entropy(b"a"*1000)==0.0

def test_uniform_byte_entropy_is_eight(): assert abs(shannon_entropy(bytes(range(256))*4)-8.0)<1e-9
