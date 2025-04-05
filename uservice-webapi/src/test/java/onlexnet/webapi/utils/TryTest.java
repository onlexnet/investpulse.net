package onlexnet.webapi.utils;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

public class TryTest {

  // Example: handle result from a supplier in normal flow
  @Test
  void shouldReturnSupplierValue() {
    var actual = switch (Try.of(() -> 1)) {
      case Try.Value<Integer>(var value) -> value;
      case Try.Failure(var ex) -> 0;
    };
    Assertions.assertThat(actual).isEqualTo(1);
  }

  // Example: handle result from a supplier when some exception will happen
  @Test
  void shouldHandleException() {
    var actual = switch (Try.of(() -> {
      throw new IllegalArgumentException();
    })) {
      case Try.Value(var value) -> value;
      case Try.Failure(var ex) -> 2;
    };
    Assertions.assertThat(actual).isEqualTo(2);
  }

  // Example: handle result from a supplier for a particular exception type
  @Test
  void shouldHandleSpecificException() {
    var actual = switch (Try.of(() -> {
      throw new IllegalArgumentException();
    })) {
      case Try.Value(var value) -> value;
      case Try.Failure(IllegalArgumentException ex) -> 2;
      case Try.Failure(Exception ex) -> 3;
    };
    Assertions.assertThat(actual).isEqualTo(2);
  }

  void someValidationMethod() {
    throw new IllegalArgumentException();
  }

  @Test
  void guardExample() {
    // invoke some validation method which can raise an exception if method params (not mentioned in the example) are invalid
    // if there is an exception -> do not continue, just return
    switch(Try.run(this::someValidationMethod)) {
      case Try.Success x -> { }
      case Try.Failure(var ex) -> { return;}
    }

    Assertions.fail("Should not be thrown as we use guard method which stops the flow");
  }
}
