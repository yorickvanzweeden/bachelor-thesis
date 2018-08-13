package nl.yorickvanzweeden.helloworld;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.support.v7.app.AppCompatActivity;
import android.view.View;

public class SecondActivity extends AppCompatActivity {
    private HelloService mService;
    private ServiceConnection mConnection;
    boolean mBound = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_second);

        findViewById(R.id.button_bind).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                bindService();
            }
        });
        findViewById(R.id.button_getHello).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new ToastDisplay(v.getContext(), mService.getContactPerson());
            }
        });
    }

    @Override
    protected void onStop() {
        super.onStop();

        if (mBound){
            unbindService(mConnection);
            mBound = false;
            findViewById(R.id.button_bind).setEnabled(true);
            findViewById(R.id.button_getHello).setEnabled(false);
        }
    }

    private void bindService(){
        mConnection = new ServiceConnection() {

            @Override
            public void onServiceConnected(ComponentName className,
                                           IBinder service) {
                HelloService.LocalBinder binder = (HelloService.LocalBinder) service;
                mService = binder.getService();
                mBound = true;
            }

            @Override
            public void onServiceDisconnected(ComponentName arg0) {
                mBound = false;
            }
        };

        Intent intent = new Intent(this, HelloService.class);
        bindService(intent, mConnection, Context.BIND_AUTO_CREATE);

        findViewById(R.id.button_bind).setEnabled(false);
        findViewById(R.id.button_getHello).setEnabled(true);
    }
}
