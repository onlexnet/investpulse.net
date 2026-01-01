package net.investpulse.x.config;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.cloud.bus.event.RefreshRemoteApplicationEvent;

import static org.assertj.core.api.Assertions.assertThatCode;

@ExtendWith(MockitoExtension.class)
class ConfigServerEventListenerTest {

    private ConfigServerEventListener listener;

    @BeforeEach
    void setUp() {
        listener = new ConfigServerEventListener();
    }

    @Test
    void shouldHandleRefreshEventSuccessfully() {
        // Given
        var event = new RefreshRemoteApplicationEvent(
                this,
                "config-server",
                "x"
        );

        // When/Then - Should not throw exception
        assertThatCode(() -> listener.handleRefreshEvent(event))
                .doesNotThrowAnyException();
    }

    @Test
    void shouldHandleRefreshEventWithWildcardDestination() {
        // Given
        var event = new RefreshRemoteApplicationEvent(
                this,
                "config-server",
                "**"
        );

        // When/Then
        assertThatCode(() -> listener.handleRefreshEvent(event))
                .doesNotThrowAnyException();
    }

    @Test
    void shouldHandleRefreshEventWithDifferentOrigins() {
        // Given - Event from different origin
        var event = new RefreshRemoteApplicationEvent(
                this,
                "another-service",
                "x"
        );

        // When/Then
        assertThatCode(() -> listener.handleRefreshEvent(event))
                .doesNotThrowAnyException();
    }

    @Test
    void shouldHandleMultipleRefreshEvents() {
        // Given
        var event1 = new RefreshRemoteApplicationEvent(this, "config-server", "x");
        var event2 = new RefreshRemoteApplicationEvent(this, "config-server", "**");
        var event3 = new RefreshRemoteApplicationEvent(this, "other-service", "x");

        // When/Then - Should handle all events
        assertThatCode(() -> {
            listener.handleRefreshEvent(event1);
            listener.handleRefreshEvent(event2);
            listener.handleRefreshEvent(event3);
        }).doesNotThrowAnyException();
    }

    @Test
    void shouldHandleRefreshEventWithEmptyOrigin() {
        // Given
        var event = new RefreshRemoteApplicationEvent(
                this,
                "",
                "x"
        );

        // When/Then
        assertThatCode(() -> listener.handleRefreshEvent(event))
                .doesNotThrowAnyException();
    }

    @Test
    void shouldHandleRefreshEventWithEmptyDestination() {
        // Given
        var event = new RefreshRemoteApplicationEvent(
                this,
                "config-server",
                ""
        );

        // When/Then
        assertThatCode(() -> listener.handleRefreshEvent(event))
                .doesNotThrowAnyException();
    }

    @Test
    void shouldLogEventDetails() {
        // Given
        var event = new RefreshRemoteApplicationEvent(
                this,
                "config-server",
                "x"
        );

        // When - Call the handler (logging happens internally)
        listener.handleRefreshEvent(event);

        // Then - Method completes (logs are not easily testable without log capture)
        // This test verifies the method executes without error
    }
}
