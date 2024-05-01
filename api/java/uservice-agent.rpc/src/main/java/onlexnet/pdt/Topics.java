package onlexnet.pdt;

public class Topics {

    private Topics() {
    }

    // schema prefix allow us to recognize our topics from other topics existing in
    // the same ecosystem
    private static final String SCHEMA_PREFIX_V1 = "onlexnet:v1";

    public static String asTopicName(Object avroEvent) {
        return SCHEMA_PREFIX_V1 + ":" + avroEvent.getClass().getCanonicalName();
    }
}
