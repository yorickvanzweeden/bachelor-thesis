package nl.yorickvanzweeden.helloworld;

import android.app.Service;
import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.os.Binder;
import android.os.IBinder;
import android.provider.ContactsContract;
import android.support.annotation.Nullable;

import java.util.Random;

public class HelloService extends Service {
    private final IBinder mBinder = new LocalBinder();
    private final Random mGenerator = new Random();
    public class LocalBinder extends Binder {
        HelloService getService() {
            return HelloService.this;
        }
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }

    public static Intent getIntent(Context context) {
        return new Intent(context, HelloService.class);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Intent i = new Intent(HelloReceiver.ACTION_SAY_HELLO);
        i.putExtra("message", getContactPerson());
        sendBroadcast(i);

        return Service.START_STICKY;
    }

    public String getContactPerson(){
        ContentResolver cr = getContentResolver();
        Cursor cur = cr.query(ContactsContract.Contacts.CONTENT_URI,
                null, null, null, null);

        if (cur.getCount() > 0) {
            int r = mGenerator.nextInt(cur.getCount() - 1);
            for (int i = 0; i < r; i++) {
                cur.moveToNext();
            }

            return cur.getString(
                    cur.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
            );
        }
        else {
            return "Yorick";
        }
    }
}
