package onlexnet.pdt;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

public class TopicsTest {

    @Test
    public void aaa() {
        var actual = Topics.asTopicName(new MyExampleClass());
        var expected = "onlexnet:v1:onlexnet.pdt.MyExampleClass";
        Assertions.assertThat(actual).isEqualTo(expected);
    }
}

class MyExampleClass {
}
