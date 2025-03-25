package onlexnet.webapi.api;

import java.time.LocalDateTime;

import lombok.Data;
import lombok.experimental.Accessors;
import onlexnet.webapi.avro.MyMessage;

@Data
@Accessors(chain = true, fluent = true)
public class TimeEvent {

    public static LocalDateTime of(MyMessage evt) {
        var date8 = evt.getDate8();
        var dd = date8 % 100;
        var MM = date8 % 10000 / 100;
        var yyyy = date8 / 10000;
        var time6 = evt.getTime6();
        var ss = time6 % 100;
        var mm = time6 % 10000 / 100;
        var hh = time6 / 10000;
        return LocalDateTime.of(yyyy, MM, dd, hh, mm, ss);
    }
    public static MyMessage of(LocalDateTime time) {
        var result = new MyMessage();
        result.setDate8(time.getYear() * 10000 + time.getMonthValue() * 100 + time.getDayOfMonth());
        result.setTime6(time.getHour() * 10000 + time.getMinute() * 100 + time.getSecond());
        return result;
    }

}
