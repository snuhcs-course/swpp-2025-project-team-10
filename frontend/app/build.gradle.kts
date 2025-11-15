import java.io.FileInputStream
import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.safeargs)
    alias(libs.plugins.kotlin.kapt)
    alias(libs.plugins.hilt)
}

android {
    namespace = "com.example.librarytogether"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.librarytogether"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

//        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        testInstrumentationRunner = "com.example.librarytogether.CustomTestRunner"

        val localProps = Properties()
        val localFile = rootProject.file("local.properties")
        if (localFile.exists()) {
            localProps.load(FileInputStream(localFile))
        }

        buildConfigField("String", "KAKAO_API_KEY", "\"${localProps.getProperty("KAKAO_API_KEY", "")}\"")
        buildConfigField("String", "GOOGLE_API_KEY", "\"${localProps.getProperty("GOOGLE_API_KEY", "")}\"")
    }

    buildTypes {
        debug {
            enableAndroidTestCoverage = true
            isTestCoverageEnabled = true
        }

        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    testOptions {
        unitTests.isReturnDefaultValues = true
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
            merges += "META-INF/LICENSE.md"
            merges += "META-INF/LICENSE-notice.md"
            merges += "META-INF/LICENSE"
            merges += "META-INF/NOTICE"
            merges += "META-INF/README"
        }
    }
}

dependencies {

    implementation(libs.flowbinding.android)
    implementation(libs.androidx.hilt.navigation.fragment)
    testImplementation(libs.hamcrest)
    testImplementation(libs.truth)
    androidTestImplementation(libs.hilt.android.testing)
    kaptAndroidTest(libs.hilt.android.compiler)
    androidTestImplementation(libs.androidx.fragment.testing)
    androidTestImplementation(libs.androidx.test.runner)
    androidTestImplementation(libs.androidx.test.rules)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.espresso.contrib)
    androidTestImplementation(libs.mockito.android)
    testImplementation(libs.kotlinx.coroutines.test)
    testImplementation(libs.mockito.core)
    testImplementation(libs.mockito.kotlin)
    testImplementation(libs.androidx.arch.core.testing)
    testImplementation(libs.junit)
    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.androidx.lifecycle.viewmodel.ktx)
    implementation(libs.androidx.lifecycle.livedata.ktx)
    coreLibraryDesugaring(libs.android.desugarJdkLibs)
    kapt (libs.glide.compiler)
    implementation (libs.glide)
    implementation (libs.androidx.viewpager2)
    implementation(libs.retrofit)
    implementation(libs.gson)
    implementation(libs.retrofit.converter.gson)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging.interceptor)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.material)
    implementation(libs.androidx.activity)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.navigation.fragment.ktx)
    implementation(libs.androidx.navigation.ui.ktx)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    implementation(libs.google.auth)
    implementation("androidx.credentials:credentials:1.6.0-alpha05")
    implementation("androidx.credentials:credentials-play-services-auth:1.6.0-alpha05")
    implementation("com.google.android.libraries.identity.googleid:googleid:1.1.0")
    implementation("com.kakao.sdk:v2-user:2.20.0")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
    implementation("de.hdodenhof:circleimageview:3.1.0")
    implementation("com.google.android.flexbox:flexbox:3.0.0")
    implementation("com.google.android.material:material:1.12.0")

    testImplementation("org.robolectric:robolectric:4.12.2")
}
